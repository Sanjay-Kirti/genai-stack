from typing import Dict, Any, List, Optional
from enum import Enum
import json
import asyncio
import logging
from datetime import datetime

from app.services.llm_service import LLMService, LLMProvider
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    USER_QUERY = "user_query"
    KNOWLEDGE_BASE = "knowledge_base"
    LLM_ENGINE = "llm_engine"
    OUTPUT = "output"
    WEB_SEARCH = "web_search"


class WorkflowEngine:
    def __init__(self):
        self.llm_service = LLMService()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService()
        self.document_service = DocumentService()
    
    async def validate_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration."""
        
        errors = []
        warnings = []
        
        # Check for required components
        nodes = workflow_config.get("nodes", [])
        edges = workflow_config.get("edges", [])
        
        if not nodes:
            errors.append("Workflow must have at least one node")
        
        # Validate node types
        valid_types = {t.value for t in ComponentType}
        for node in nodes:
            # Check both node.type and node.data.type for compatibility
            node_type = node.get("type")
            if node_type == "custom":
                # For custom nodes, get type from data
                node_type = node.get("data", {}).get("type")
            
            if node_type not in valid_types:
                errors.append(f"Invalid node type: {node_type}")
        
        # Check for user_query and output nodes
        has_input = any(
            n.get("type") == ComponentType.USER_QUERY.value or 
            n.get("data", {}).get("type") == ComponentType.USER_QUERY.value 
            for n in nodes
        )
        has_output = any(
            n.get("type") == ComponentType.OUTPUT.value or 
            n.get("data", {}).get("type") == ComponentType.OUTPUT.value 
            for n in nodes
        )
        
        if not has_input:
            errors.append("Workflow must have at least one User Query node")
        if not has_output:
            errors.append("Workflow must have at least one Output node")
        
        # Validate connections
        node_ids = {n.get("id") for n in nodes}
        for edge in edges:
            if edge.get("source") not in node_ids:
                errors.append(f"Invalid edge source: {edge.get('source')}")
            if edge.get("target") not in node_ids:
                errors.append(f"Invalid edge target: {edge.get('target')}")
        
        # Check for API keys if LLM nodes are present
        llm_nodes = [
            n for n in nodes 
            if n.get("type") == ComponentType.LLM_ENGINE.value or 
            n.get("data", {}).get("type") == ComponentType.LLM_ENGINE.value
        ]
        for llm_node in llm_nodes:
            config = llm_node.get("data", {}).get("config", {})
            if not config.get("apiKey"):
                warnings.append(f"LLM node {llm_node.get('id')} missing API key")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def execute_workflow(
        self,
        workflow_config: Dict[str, Any],
        user_input: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a workflow with given user input."""
        
        # Validate workflow first
        validation = await self.validate_workflow(workflow_config)
        if not validation["valid"]:
            raise ValueError(f"Invalid workflow: {validation['errors']}")
        
        nodes = workflow_config.get("nodes", [])
        edges = workflow_config.get("edges", [])
        
        # Build execution graph
        execution_graph = self._build_execution_graph(nodes, edges)
        
        # Initialize execution context
        context = {
            "user_input": user_input,
            "session_id": session_id,
            "results": {},
            "metadata": {
                "start_time": datetime.utcnow().isoformat(),
                "workflow_id": workflow_config.get("id")
            }
        }
        
        # Execute nodes in topological order
        executed_nodes = set()
        
        while len(executed_nodes) < len(nodes):
            # Find nodes that can be executed
            ready_nodes = []
            for node in nodes:
                node_id = node.get("id")
                if node_id in executed_nodes:
                    continue
                
                # Check if all dependencies are satisfied
                dependencies = execution_graph.get(node_id, {}).get("dependencies", [])
                if all(dep in executed_nodes for dep in dependencies):
                    ready_nodes.append(node)
            
            if not ready_nodes:
                break
            
            # Execute ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                tasks.append(self._execute_node(node, context))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results and mark nodes as executed
            for node, result in zip(ready_nodes, results):
                node_id = node.get("id")
                if isinstance(result, Exception):
                    logger.error(f"Error executing node {node_id}: {str(result)}")
                    context["results"][node_id] = {"error": str(result)}
                else:
                    context["results"][node_id] = result
                executed_nodes.add(node_id)
        
        # Prepare final output
        output_nodes = [
            n for n in nodes 
            if n.get("type") == ComponentType.OUTPUT.value or 
            n.get("data", {}).get("type") == ComponentType.OUTPUT.value
        ]
        final_output = []
        
        for output_node in output_nodes:
            node_id = output_node.get("id")
            if node_id in context["results"]:
                final_output.append(context["results"][node_id])
        
        context["metadata"]["end_time"] = datetime.utcnow().isoformat()
        
        return {
            "output": final_output,
            "context": context,
            "execution_summary": {
                "total_nodes": len(nodes),
                "executed_nodes": len(executed_nodes),
                "errors": sum(1 for r in context["results"].values() if "error" in r)
            }
        }
    
    def _build_execution_graph(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Build execution graph from nodes and edges."""
        
        graph = {}
        
        # Initialize graph with nodes
        for node in nodes:
            node_id = node.get("id")
            graph[node_id] = {
                "node": node,
                "dependencies": [],
                "dependents": []
            }
        
        # Add edges
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            
            if source in graph and target in graph:
                graph[target]["dependencies"].append(source)
                graph[source]["dependents"].append(target)
        
        return graph
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow node."""
        
        # Handle custom node types from React Flow
        node_type = node.get("type")
        if node_type == "custom":
            node_type = node.get("data", {}).get("type")
        
        node_data = node.get("data", {})
        config = node_data.get("config", {})
        
        try:
            if node_type == ComponentType.USER_QUERY.value:
                return await self._execute_user_query(node, context)
            
            elif node_type == ComponentType.KNOWLEDGE_BASE.value:
                return await self._execute_knowledge_base(node, context)
            
            elif node_type == ComponentType.LLM_ENGINE.value:
                return await self._execute_llm_engine(node, context)
            
            elif node_type == ComponentType.WEB_SEARCH.value:
                return await self._execute_web_search(node, context)
            
            elif node_type == ComponentType.OUTPUT.value:
                return await self._execute_output(node, context)
            
            else:
                raise ValueError(f"Unknown node type: {node_type}")
                
        except Exception as e:
            logger.error(f"Error executing node {node.get('id')}: {str(e)}")
            raise
    
    async def _execute_user_query(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute user query node."""
        
        return {
            "type": "user_query",
            "content": context["user_input"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_knowledge_base(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute knowledge base node."""
        
        config = node.get("data", {}).get("config", {})
        
        # Search in vector store
        search_results = await self.vector_store_service.search_by_text(
            query_text=context["user_input"],
            embedding_service=self.embedding_service,
            n_results=config.get("topK", 5),
            provider=config.get("embeddingProvider", "openai")
        )
        
        return {
            "type": "knowledge_base",
            "documents": search_results.get("documents", []),
            "relevance_scores": search_results.get("distances", []),
            "metadata": search_results.get("metadatas", [])
        }
    
    async def _execute_llm_engine(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute LLM engine node."""
        
        config = node.get("data", {}).get("config", {})
        
        # Prepare prompt with context
        prompt = context["user_input"]
        
        # Add knowledge base context if available
        kb_results = None
        for result in context["results"].values():
            if result.get("type") == "knowledge_base":
                kb_results = result
                break
        
        if kb_results and kb_results.get("documents"):
            context_docs = "\n\n".join(kb_results["documents"][:3])
            prompt = f"Context:\n{context_docs}\n\nQuestion: {prompt}"
        
        # Add custom prompt if provided
        if config.get("prompt"):
            prompt = config["prompt"].replace("{query}", prompt)
        
        # Determine provider
        provider = LLMProvider.OPENAI
        model_name = config.get("model", "").lower()
        if "gemini" in model_name:
            provider = LLMProvider.GEMINI
        
        # Generate completion
        response = await self.llm_service.generate_completion(
            prompt=prompt,
            provider=provider,
            model=config.get("model"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("maxTokens", 1000),
            system_prompt=config.get("systemPrompt"),
            api_key=config.get("apiKey")
        )
        
        return {
            "type": "llm_response",
            "content": response,
            "model": config.get("model"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_web_search(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute web search node."""
        
        # This would integrate with a web search API
        # For now, returning a placeholder
        return {
            "type": "web_search",
            "results": [],
            "query": context["user_input"],
            "message": "Web search integration coming soon"
        }
    
    async def _execute_output(
        self,
        node: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute output node."""
        
        # Collect outputs from connected nodes
        output_content = []
        
        for result in context["results"].values():
            if result.get("type") == "llm_response":
                output_content.append(result.get("content", ""))
        
        return {
            "type": "output",
            "content": "\n\n".join(output_content) if output_content else "No output generated",
            "timestamp": datetime.utcnow().isoformat()
        }
