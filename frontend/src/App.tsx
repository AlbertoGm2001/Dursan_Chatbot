// Indica que este componente se ejecuta en el cliente (React Server Components)
"use client"
import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Heart, Star } from "lucide-react"
import type { JSX } from "react/jsx-runtime" // Importa JSX para evitar errores de variable no declarada


//Objetivo:
//Mandar una petición a la api la cual envía como cuerpo un diccionario con los mensajes recibidos por el usuario

interface RecommendationRequest {
  chat_questions: string[];
  user_answers: string[];
}

// Define la estructura de un mensaje en el chat
interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

// Lista de coches de ejemplo para mostrar recomendaciones


// Preguntas que la IA hará al usuario para personalizar la recomendación
const AI_QUESTIONS: string[] = [
  "¡Hola! Estoy aquí para ayudarte a encontrar el coche perfecto. ¿Cuál es tu nombre?",
  "¡Encantado de conocerte! ¿Tienes alguna marca de coche favorita?",
  "¿Cuál es tu rango de presupuesto para esta compra?",
  "¿Te interesan los vehículos eléctricos o híbridos?",
  "¿Para qué usarás principalmente este coche? (Desplazamientos diarios, viajes familiares, etc.)",
  "¿Hay alguna característica específica que sea importante para ti?",
  "¡Perfecto! Déjame encontrar las mejores opciones para ti...",
]


export default function CarChatApp(): JSX.Element {
  // Estado para los mensajes del chat
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: AI_QUESTIONS[0],
      isUser: false,
      timestamp: new Date(),
    },
  ])
  // Estado para el input actual del usuario
  const [currentInput, setCurrentInput] = useState<string>("")
  // Estado para saber en qué pregunta va la IA
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0)
  // Estado para mostrar las recomendaciones de coches
  const [showRecommendations, setShowRecommendations] = useState<boolean>(false)
  // Estado para mostrar animación de "escribiendo"
  const [isTyping, setIsTyping] = useState<boolean>(false)
  // Referencia para hacer scroll automático al final del chat
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Hace scroll automático al último mensaje
  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // Efecto para hacer scroll cada vez que cambian los mensajes
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Simula el tiempo de respuesta de la IA mostrando animación de "escribiendo"
  const simulateTyping = (content: string, callback: () => void): void => {
    setIsTyping(true)
    setTimeout(() => {
      setIsTyping(false)
      const newMessage: Message = {
        id: Date.now().toString(),
        content,
        isUser: false,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, newMessage])
      callback()
    }, 150)
  }

  // Maneja el envío de mensajes del usuario
  const handleSendMessage = (): void => {
    if (!currentInput.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: currentInput,
      isUser: true,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setCurrentInput("")

    const nextQuestionIndex = currentQuestionIndex + 1

    // Si hay más preguntas, la IA responde con la siguiente
    if (nextQuestionIndex < AI_QUESTIONS.length) {
      simulateTyping(AI_QUESTIONS[nextQuestionIndex], () => {
        setCurrentQuestionIndex(nextQuestionIndex)
        // Si es la última pregunta, muestra recomendaciones
        if (nextQuestionIndex === AI_QUESTIONS.length - 1) {
          setTimeout(() => {
            setShowRecommendations(true)
          }, 1000)
        }
      })
    }
  }

  // Permite enviar mensaje con la tecla Enter
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter") {
      handleSendMessage()
    }
  }

  const sendMessagesToApi = ():void=>{

    const userMessages = messages.filter(msg => msg.isUser).map(msg => msg.content)
    const recommendationRequest: RecommendationRequest = {
      chat_questions: userMessages,
      user_answers: userMessages
    }
    fetch("http://localhost:8000/get_recommendations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(recommendationRequest)
    })
    .then(response => response.json())
    .then(data => {
      console.log("Respuesta de la API:", data)
    })
    .catch(error => {
      console.error("Error al enviar mensajes a la API:", error)
    })
  }

  // Llama a la función para enviar mensajes a la API solo cuando showRecommendations es true
  useEffect(() => {
    if (showRecommendations) {
      sendMessagesToApi()
    }
  }, [showRecommendations])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header: Encabezado de la app */}
      <div className="border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              {/* Aquí podría ir un icono de coche */}
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">DURSAN AI</h1>
              <p className="text-sm text-gray-600">Tu asistente personal de recomendación de coches</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container: Contenedor principal del chat */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="space-y-4 mb-6">
          {/* Renderiza los mensajes del chat */}
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.isUser
                    ? "bg-blue-600 text-white ml-4"
                    : "bg-white text-gray-900 mr-4 border border-gray-200 shadow-sm"
                }`}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
                <p className={`text-xs mt-2 opacity-70`}>
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </div>
          ))}

          {/* Animación de "IA está escribiendo..." */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-900 mr-4 border border-gray-200 shadow-sm rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">IA está escribiendo...</span>
                </div>
              </div>
            </div>
          )}

          {/* Referencia para el scroll automático */}
          <div ref={messagesEndRef} />
        </div>

        {/* Car Recommendations: Sección de recomendaciones de coches */}
        {showRecommendations && (
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Star className="w-6 h-6 text-blue-600" />
              Opciones Perfectas para Ti
            </h2>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            
            </div>
          </div>
        )}

        {/* Input Area: Zona de entrada de texto para el usuario */}
        {!showRecommendations && (
          <div className="sticky bottom-0 bg-gray-50/80 backdrop-blur-sm border-t border-gray-200 pt-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={currentInput}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu respuesta..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isTyping}
              />
              {/* Botón para enviar mensaje */}
              <button
                onClick={handleSendMessage}
                disabled={!currentInput.trim() || isTyping}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-2 rounded-md transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
