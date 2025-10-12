// Indica que este componente se ejecuta en el cliente (React Server Components)
"use client"
import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Heart, Star } from "lucide-react"
import "./App.css"
import type { JSX } from "react/jsx-runtime"

interface CarRecommendation {
  id: number;
  url: string;
  car_brand: string;
  car_model: string;
  description: string;
  offer_price: number;
  monthly_offer_price: number;
  car_year: number;
  car_kms: number;
  automatic: boolean | number;
  fuel_type: string;
  fit_reasoning: string;
}


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
  
  // Add header with logo and title
  const renderHeader = () => (
    <header className="header">
      <div className="header-inner">
        <div className="header-logo">
          <img src="/images/dursan_logo.jpeg" alt="Dursan Logo" />
        </div>
        <h1 className="header-title">DURSAN AI</h1>
      </div>
    </header>
  )
  // Estado para el input actual del usuario
  const [currentInput, setCurrentInput] = useState<string>("")
  // Estado para saber en qué pregunta va la IA
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0)
  // Estado para mostrar las recomendaciones de coches
  const [showRecommendations, setShowRecommendations] = useState<boolean>(false)
  // Estado para almacenar las recomendaciones
  const [recommendations, setRecommendations] = useState<CarRecommendation[]>([])
  // Estado para mostrar animación de "escribiendo"
  const [isTyping, setIsTyping] = useState<boolean>(false)
  // Estado para mostrar animación de búsqueda de recomendaciones
  const [isSearchingRecommendations, setIsSearchingRecommendations] = useState<boolean>(false)
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
    setIsSearchingRecommendations(true)
    fetch("http://localhost:8000/get_recommendations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(recommendationRequest)
    })
    .then(response => response.json())
    .then(data => {
      setRecommendations(data.recommendations || [])
      setIsSearchingRecommendations(false)
    })
    .catch(error => {
      console.error("Error al enviar mensajes a la API:", error)
      setIsSearchingRecommendations(false)
    })
  }

  // Llama a la función para enviar mensajes a la API solo cuando showRecommendations es true
  useEffect(() => {
    if (showRecommendations) {
      sendMessagesToApi()
    }
  }, [showRecommendations])

  return (
    <div className="min-h-screen">
      {/* Header: Encabezado de la app */}
      <div className="header">
        <div className="header-inner">
          <div className="header-logo">
            <img src="/images/dursan_logo.jpeg" alt="Dursan Logo" />
          </div>
          <div>
            <div className="header-title">DURSAN AI</div>
            <div className="header-desc">Tu asistente personal de recomendación de coches</div>
          </div>
        </div>
      </div>

      {/* Chat Container: Contenedor principal del chat */}
      <div className="chat-container">
        <div className="chat-messages">
          {/* Renderiza los mensajes del chat */}
          {messages.map((message) => (
            <div key={message.id} style={{ display: 'flex', justifyContent: message.isUser ? 'flex-end' : 'flex-start' }}>
              <div className={`chat-bubble ${message.isUser ? 'user' : 'ai'}`}>
                {message.content}
                <div className="chat-timestamp">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </div>
          ))}

          {/* Animación de "IA está escribiendo..." */}
          {isTyping && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div className="typing-indicator">
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span className="typing-dot"></span>
                <span style={{ marginLeft: 8, color: '#6b7280', fontSize: '0.98rem' }}>IA está escribiendo...</span>
              </div>
            </div>
          )}

          {/* Referencia para el scroll automático */}
          <div ref={messagesEndRef} />
        </div>

        {/* Car Recommendations: Sección de recomendaciones de coches */}
        {showRecommendations && isSearchingRecommendations && (
          <div className="searching-recommendations">
            <h2 className="searching-recommendations-title">Buscando las Mejores Opciones</h2>
            <div className="searching-recommendations-icon">
              <div className="searching-recommendations-spinner"></div>
            </div>
            <p className="searching-recommendations-text">
              Analizando tus preferencias para encontrar los coches perfectos para ti...
            </p>
          </div>
        )}
        {showRecommendations && !isSearchingRecommendations && (
          <div style={{ marginBottom: 32 }}>
            <div className="recommendations-title">
              <Star style={{ width: 28, height: 28, color: '#2563eb' }} />
              Opciones Perfectas para Ti
            </div>
            <div className="recommendations-grid">
              {recommendations.map((rec) => (
                <div key={rec.id} className="car-card">
                  <a href={rec.url} target="_blank" rel="noopener noreferrer">
                    Ver en Dursan
                  </a>
                  <div className="car-brand">{rec.car_brand} <span className="car-model">{rec.car_model}</span></div>
                  <div className="car-description">{rec.description}</div>
                  <div className="car-tags">
                    <span className="car-tag">Año: {rec.car_year}</span>
                    <span className="car-tag">Kms: {rec.car_kms.toLocaleString()}</span>
                    <span className="car-tag">{rec.automatic ? "Automático" : "Manual"}</span>
                    <span className="car-tag">{rec.fuel_type}</span>
                  </div>
                  <div className="car-price">{rec.offer_price.toLocaleString()} €</div>
                  <div className="car-monthly">Desde {rec.monthly_offer_price.toLocaleString()} €/mes</div>
                  <div className="fit-reasoning">{rec.fit_reasoning}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Area: Zona de entrada de texto para el usuario */}
        {!showRecommendations && (
          <div className="input-area">
            <div className="input-row">
              <input
                type="text"
                value={currentInput}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu respuesta..."
                disabled={isTyping}
              />
              {/* Botón para enviar mensaje */}
              <button
                onClick={handleSendMessage}
                disabled={!currentInput.trim() || isTyping}
              >
                <Send style={{ width: 20, height: 20 }} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
