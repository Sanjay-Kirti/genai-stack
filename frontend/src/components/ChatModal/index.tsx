import { useState, useEffect, useRef, Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { X, Send, Loader2, Bot, User } from 'lucide-react'
import { ChatMessage } from '@/types'
import { createWebSocketConnection } from '@/services/api'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface ChatModalProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  workflowName: string
}

export default function ChatModal({ isOpen, onClose, sessionId, workflowName }: ChatModalProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (sessionId && isOpen) {
      console.log('Creating WebSocket connection for session:', sessionId)
      const websocket = createWebSocketConnection(sessionId)
      
      websocket.onopen = () => {
        console.log('WebSocket connected successfully')
        setWs(websocket)
      }

      websocket.onmessage = (event) => {
        console.log('WebSocket message received:', event.data)
        const data = JSON.parse(event.data)
        
        if (data.type === 'user_message') {
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            session_id: sessionId,
            role: 'user',
            content: data.message,
            created_at: data.timestamp,
          }
          setMessages((prev) => [...prev, newMessage])
        } else if (data.type === 'assistant_message') {
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            session_id: sessionId,
            role: 'assistant',
            content: data.message,
            created_at: data.timestamp,
          }
          setMessages((prev) => [...prev, newMessage])
        } else if (data.type === 'thinking') {
          setIsThinking(data.status)
        } else if (data.type === 'error') {
          toast.error(data.message)
          setIsThinking(false)
        }
      }

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
        toast.error('Connection error. Please try again.')
        setWs(null)
      }

      websocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        setWs(null)
      }

      return () => {
        console.log('Cleaning up WebSocket connection')
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.close()
        }
      }
    } else {
      setWs(null)
    }
  }, [sessionId, isOpen])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !ws || ws.readyState !== WebSocket.OPEN) return

    ws.send(JSON.stringify({ message: inputMessage }))
    setInputMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white border border-gray-200 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <Bot className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <Dialog.Title className="text-lg font-semibold text-gray-900">
                        GenAI Stack Chat
                      </Dialog.Title>
                      <p className="text-sm text-gray-500">{workflowName}</p>
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Messages */}
                <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
                  {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                      <Bot className="w-16 h-16 text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Start a conversation to test your stack
                      </h3>
                      <p className="text-sm text-gray-500">
                        Type a message below to begin chatting with your AI workflow
                      </p>
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        'flex gap-3',
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {message.role === 'assistant' && (
                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <Bot className="w-5 h-5 text-green-600" />
                        </div>
                      )}
                      <div
                        className={cn(
                          'max-w-[70%] rounded-lg px-4 py-3',
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-white border border-gray-200 text-gray-900'
                        )}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                      {message.role === 'user' && (
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <User className="w-5 h-5 text-blue-600" />
                        </div>
                      )}
                    </div>
                  ))}

                  {isThinking && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <Bot className="w-5 h-5 text-green-600" />
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Loader2 className="w-4 h-4 animate-spin text-green-600" />
                          <span className="text-sm text-gray-600">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-6 border-t border-gray-200 bg-white">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Send a message..."
                      className="flex-1 input"
                      disabled={isThinking || !ws || ws.readyState !== WebSocket.OPEN}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isThinking || !ws || ws.readyState !== WebSocket.OPEN}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {isThinking ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Send className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
