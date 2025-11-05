// Indica que este componente se ejecuta en el cliente (React Server Components)
"use client"
import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Star } from "lucide-react"
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
  image_url: string;
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
  "¡Hola! Antes de empezar a buscar el coche perfecto para ti, me gustaría saber: ¿cuál es tu presupuesto máximo para esta compra?",
  "Perfecto, pues empezamos con las preguntas: ¿Tienes alguna marca de coche favorita?",
  "¿Para qué tipo de trayectos sueles usar el coche?(Viajes largos, trayectos por ciudad, un poco de todo...)?",
  "¿Te gustaría que fuera automático o te da igual?",
  "¿Sueles viajar solo o acompañado?",
  "¿Qué opinas acerca de los coches eléctricos o híbridos?",
  "Para finalizar, ¿Hay alguna característica específica que sea importante para ti?",
  "¡Perfecto! Déjame encontrar las mejores opciones para ti...",
]
const API_ENV = 'SERVER'
const API_URL = API_ENV === 'LOCAL' ? 'http://localhost:8000' : 'https://dursan-chatbot.onrender.com/'
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
  // Estado para el slider del presupuesto
  const [budgetValue, setBudgetValue] = useState<number>(25000)
  // Estado para el tipo de pago (una vez o mensual)
  const [paymentType, setPaymentType] = useState<'once' | 'monthly'>('once')
  // Estado para el valor mensual
  const [monthlyValue, setMonthlyValue] = useState<number>(300)
  // Estado para mostrar las recomendaciones de coches
  const [showRecommendations, setShowRecommendations] = useState<boolean>(false)
  // Estado para almacenar las recomendaciones
  const [recommendations, setRecommendations] = useState<CarRecommendation[]>([])
  // Estado para mostrar animación de "escribiendo"
  const [isTyping, setIsTyping] = useState<boolean>(false)
  // Estado para mostrar animación de búsqueda de recomendaciones
  const [isSearchingRecommendations, setIsSearchingRecommendations] = useState<boolean>(false)
  // Estado para manejar errores de la API
  const [apiError, setApiError] = useState<string | null>(null)
  // Estado para distinguir si es un error 404 (no hay resultados) o un error real
  const [is404Error, setIs404Error] = useState<boolean>(false)
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
    let messageContent = currentInput.trim()
    
    // Si es la pregunta del presupuesto, usar el valor del slider
    if (currentQuestionIndex === 0) {
      if (paymentType === 'once') {
        if (budgetValue >= 100000) {
          messageContent = `No me importa pagar más de 100.000 euros`
        } else {
          messageContent = `Mi presupuesto máximo es de ${budgetValue.toLocaleString()} € (pago único)`
        }
      } else {
        if (monthlyValue >= 1000) {
          messageContent = `No me importa pagar más de 1.000 €/mes`
        } else {
          messageContent = `Prefiero pagar máximo ${monthlyValue.toLocaleString()} €/mes`
        }
      }
    }
    
    if (!messageContent) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageContent,
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
      chat_questions: AI_QUESTIONS.slice(0, -1),
      user_answers: userMessages
    }
    setIsSearchingRecommendations(true)
    setApiError(null) // Clear any previous errors
    setIs404Error(false) // Clear previous 404 flag
    fetch(`${API_URL}/get_recommendations`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(recommendationRequest)
    })
    .then(response => {
      if (response.ok) {
        return response.json()
      }
      else if (response.status === 404) {
        // Mark as 404 error and try to get the error message from the API response
        return response.json().then(errorData => {
          const error = new Error(errorData.message || "No hemos conseguido encontrar ninguna oferta que se ajuste a tus necesidades.")
          error.name = "404Error"
          throw error
        }).catch(() => {
          const error = new Error("No hemos conseguido encontrar ninguna oferta que se ajuste a tus necesidades.")
          error.name = "404Error"
          throw error
        })
      }
      throw new Error("Error interno del servidor. Inténtelo de nuevo más tarde.")
    })
    .then(data => {
      setRecommendations(data.recommendations || [])
      setIsSearchingRecommendations(false)
      setApiError(null) // Clear error on success
      setIs404Error(false) // Clear 404 flag on success
    })
    .catch(error => {

      console.error("Error al enviar mensajes a la API:", error)
      setIsSearchingRecommendations(false)
      
      // Check if it's a 404 error
      if (error.name === "404Error") {
        setIs404Error(true)
        setApiError(error.message)
      } else if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        setIs404Error(false)
        setApiError("No se pudo conectar con el servidor. Verifica tu conexión o inténtalo más tarde.")
      } else {
        setIs404Error(false)
        setApiError(error.message || "Ha ocurrido un error inesperado.")
      }
    })
  }

  // Function to refresh the page
  const refreshPage = ():void => {
    window.location.reload()
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
        {showRecommendations && !isSearchingRecommendations && apiError && (
          <div className={is404Error ? "no-results-container" : "error-container"}>
            <div className={is404Error ? "no-results-icon" : "error-icon"}>
              {is404Error ? "🔍" : "⚠️"}
            </div>
            <h3 className={is404Error ? "no-results-title" : "error-title"}>
              {is404Error ? "No hemos encontrado ofertas para ti" : "Ups, algo ha salido mal"}
            </h3>
            <p className={is404Error ? "no-results-message" : "error-message"}>{apiError}</p>
            <div className={is404Error ? "no-results-actions" : "error-actions"}>
              <button className={is404Error ? "no-results-retry-btn" : "error-retry-btn"} onClick={refreshPage}>
                {is404Error ? "Empezar de nuevo" : "Intentar de nuevo"}
              </button>
            </div>
          </div>
        )}
        {showRecommendations && !isSearchingRecommendations && !apiError && (
          <div style={{ marginBottom: 32 }}>
            <div className="recommendations-title">
              <Star style={{ width: 28, height: 28, color: '#2563eb' }} />
              Opciones Perfectas para Ti
            </div>
            <div className="recommendations-grid">
              {recommendations.map((rec) => (
                <div key={rec.id} className="car-card">
                  {rec.image_url && (
                    <div className="car-image">
                      <img src={`images/car_images/${rec.image_url}`} alt={`${rec.car_brand} ${rec.car_model}`} />
                    </div>
                  )}
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
            {currentQuestionIndex === 0 ? (
              // Slider para la pregunta del presupuesto
              <div className="budget-slider-container">
                {/* Selección de tipo de pago */}
                <div className="payment-type-selector">
                  <div className="payment-type-label">¿Cómo prefieres pagar?</div>
                  <div className="payment-type-buttons">
                    <button
                      type="button"
                      className={`payment-type-btn ${paymentType === 'once' ? 'active' : ''}`}
                      onClick={() => setPaymentType('once')}
                      disabled={isTyping}
                    >
                      Pago único
                    </button>
                    <button
                      type="button"
                      className={`payment-type-btn ${paymentType === 'monthly' ? 'active' : ''}`}
                      onClick={() => setPaymentType('monthly')}
                      disabled={isTyping}
                    >
                      Cuota mensual
                    </button>
                  </div>
                </div>

                {/* Display del valor seleccionado */}
                <div className="budget-display">
                  <span className="budget-label">
                    {paymentType === 'once' ? 'Presupuesto máximo:' : 'Cuota mensual máxima:'}
                  </span>
                  <span className="budget-value">
                    {paymentType === 'once' 
                      ? (budgetValue >= 100000 ? '>100.000 €' : `${budgetValue.toLocaleString()} €`)
                      : (monthlyValue >= 1000 ? '>1.000 €/mes' : `${monthlyValue.toLocaleString()} €/mes`)
                    }
                  </span>
                </div>

                {/* Slider condicional */}
                <div className="slider-wrapper">
                  {paymentType === 'once' ? (
                    <>
                      <input
                        type="range"
                        min="5000"
                        max="100000"
                        step="1000"
                        value={budgetValue}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBudgetValue(Number(e.target.value))}
                        className="budget-slider"
                        disabled={isTyping}
                      />
                      <div className="slider-labels">
                        <span>5.000 €</span>
                        <span>100.000 €</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <input
                        type="range"
                        min="80"
                        max="1000"
                        step="20"
                        value={monthlyValue}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMonthlyValue(Number(e.target.value))}
                        className="budget-slider"
                        disabled={isTyping}
                      />
                      <div className="slider-labels">
                        <span>80 €/mes</span>
                        <span>1.000 €/mes</span>
                      </div>
                    </>
                  )}
                </div>

                <button
                  onClick={handleSendMessage}
                  disabled={isTyping}
                  className="budget-submit-btn"
                >
                  <Send style={{ width: 20, height: 20 }} />
                  Confirmar presupuesto
                </button>
              </div>
            ) : (
              // Input de texto normal para otras preguntas
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
            )}
          </div>
        )}
      </div>
    </div>
  )
}
