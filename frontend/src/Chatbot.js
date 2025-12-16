import React, { useState } from "react";
import { GoogleGenerativeAI } from "@google/generative-ai";

// --- Gemini System Instructions
const SYSTEM_INSTRUCTIONS = `
You are a friendly, domain specific real estate assistant for a property comparison application.

GREETING BEHAVIOR:
- When the conversation starts, greet the user politely.
- Introduce yourself briefly as a property comparison assistant.
- Do not greet repeatedly in every response.

STRICT RESPONSE RULES:
- Respond using clear, natural English sentences only.
- Do NOT use bullet points, numbered lists, IDs, markdown, or catalog style formatting.
- Do NOT format responses like property listings or inventories.
- Do NOT invent property IDs, titles, prices, or any missing information.
- Do NOT use special symbols such as **, -, or numbered points.

CONTENT RULES:
- Base all answers strictly on the provided property data.
- When two properties are available, focus on comparing them clearly.
- If the user asks something unrelated to the properties, politely refuse.
- If required information is missing, clearly say that you do not have enough data.

STYLE GUIDELINES:
- Conversational and professional
- Clear and concise
- Human sounding and easy to understand
- Neutral and unbiased in tone

If a question cannot be answered using the provided data, respond by saying you do not have enough information to answer it.
`;

// --- API Configuration ---
const genAI = new GoogleGenerativeAI(
  process.env.REACT_APP_GEMINI_API_KEY
);

const model = genAI.getGenerativeModel({
  model: "gemini-2.5-flash"
});

// --- Chatbot Component ---

const Chatbot = ({ prop1, prop2 }) => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hi! Ask me anything about the compared properties."
    }
  ]);
  // State for the user's current input text and thinking.
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  //Constructs the property data context that is injected into the prompt.
  // This is currently using hardcoded mock data for demonstration. 

  const buildContext = () => {
    // If props are missing, instruct the AI that there is no data.
    if (!prop1 || !prop2) {
      return "No properties selected yet.";
    }

    return `
You are a real estate assistant.
Answer ONLY using the following data.

Available property data:

Property 1:
Title: 3 BHK Apartment in Downtown
Location: New York, NY
Price: 450000
Bedrooms: 3
Bathrooms: 2
Size: 1500 sqft
Amenities: Gym, Swimming Pool, Parking

Property 2:
Title: 2 BHK Condo with Sea View
Location: Miami, FL
Price: 380000
Bedrooms: 2
Bathrooms: 2
Size: 1200 sqft
Amenities: Beach Access, Security, Balcony

Property 3:
Title: Luxury Villa with Private Garden
Location: Los Angeles, CA
Price: 850000
Bedrooms: 4
Bathrooms: 3
Size: 2800 sqft
Amenities: Private Garden, Smart Home, Garage

Property 4:
Title: 1 BHK Budget Apartment
Location: Austin, TX
Price: 250000
Bedrooms: 1
Bathrooms: 1
Size: 800 sqft
Amenities: Gym, Laundry, Security

Property 5:
Title: Penthouse with Skyline View
Location: San Francisco, CA
Price: 1200000
Bedrooms: 5
Bathrooms: 4
Size: 3500 sqft
Amenities: Rooftop Terrace, Smart Security, Private Elevator

Property 6:
Title: Cozy Studio in Central Park
Location: New York, NY
Price: 300000
Bedrooms: 1
Bathrooms: 1
Size: 600 sqft
Amenities: Park View, 24/7 Concierge, Fitness Center

Property 7:
Title: Lakefront House with Dock
Location: Chicago, IL
Price: 750000
Bedrooms: 3
Bathrooms: 2
Size: 2000 sqft
Amenities: Private Dock, Boat Parking, BBQ Area

Property 8:
Title: Modern Townhouse with Backyard
Location: Dallas, TX
Price: 600000
Bedrooms: 3
Bathrooms: 3
Size: 1800 sqft
Amenities: Backyard, Community Pool, Pet Friendly

Property 9:
Title: 4 BHK Duplex with Home Office
Location: Seattle, WA
Price: 920000
Bedrooms: 4
Bathrooms: 3
Size: 2500 sqft
Amenities: Home Office, Solar Panels, Two-Car Garage

Property 10:
Title: Minimalist Smart Home
Location: Boston, MA
Price: 700000
Bedrooms: 3
Bathrooms: 2
Size: 1900 sqft
Amenities: Minimalist Design, Smart Appliances, Energy Efficient


If you do not have enough data, say so.
`;
  };
// Handles sending the user's message to the Gemini API.
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");

    setMessages(prev => [
      ...prev,
      { role: "user", text: userMessage }
    ]);

    setLoading(true);

    try {
      const prompt = `${SYSTEM_INSTRUCTIONS} Context: ${buildContext()} User question: ${userMessage}`;
      // Call the Gemini API to generate content based on the structured prompt
      const result = await model.generateContent(prompt);
      const response = result.response.text();

      setMessages(prev => [
        ...prev,
        { role: "bot", text: response }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: "bot",
          text: "Sorry, something went wrong. Please try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 bg-green-700 text-white rounded-full w-14 h-14 flex items-center justify-center shadow-lg text-2xl"
      >
        💬
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 w-[360px] bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden">
          <div className="bg-green-700 text-white px-4 py-3 font-bold">
            Property Assistant
          </div>

          <div className="flex-1 p-4 space-y-3 overflow-y-auto bg-gray-50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                  msg.role === "user"
                    ? "bg-green-600 text-white ml-auto"
                    : "bg-white text-gray-800 border"
                }`}
              >
                {msg.text}
              </div>
            ))}

            {loading && (
              <div className="text-sm text-gray-500">
                Thinking...
              </div>
            )}
          </div>

          <div className="p-3 border-t flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none"
              onKeyDown={e => e.key === "Enter" && handleSend()}
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="bg-green-700 text-white px-4 py-2 rounded-md text-sm font-semibold disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;
