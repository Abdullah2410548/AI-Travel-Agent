import os
from dotenv import load_dotenv
import chainlit as cl
from typing import cast, List, Dict, Optional
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, handoff
from agents.run import RunConfig, RunContextWrapper
import json
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# Travel Tools with Mock Data
async def get_flights(origin: str, destination: str, departure_date: str, return_date: str = None) -> str:
    """Get flight options between two cities with mock data."""
    
    # Mock flight data
    airlines = ["Emirates", "Qatar Airways", "Turkish Airlines", "Lufthansa", "British Airways", "Air France"]
    flight_times = ["06:00", "09:30", "14:15", "18:45", "22:30"]
    
    flights = []
    for i in range(3):  # Generate 3 flight options
        airline = random.choice(airlines)
        departure_time = random.choice(flight_times)
        arrival_time = random.choice(flight_times)
        price = random.randint(300, 1500)
        duration = f"{random.randint(2, 15)}h {random.randint(0, 59)}m"
        
        flight = {
            "airline": airline,
            "flight_number": f"{airline[:2].upper()}{random.randint(100, 999)}",
            "departure": f"{departure_time} from {origin}",
            "arrival": f"{arrival_time} to {destination}",
            "price": f"${price}",
            "duration": duration,
            "stops": random.choice(["Direct", "1 Stop", "2 Stops"])
        }
        flights.append(flight)
    
    # Format response
    flight_info = f"✈️ **Flight Options: {origin} → {destination}**\n"
    flight_info += f"📅 **Departure Date:** {departure_date}\n\n"
    
    for i, flight in enumerate(flights, 1):
        flight_info += f"**Option {i}:**\n"
        flight_info += f"• {flight['airline']} - {flight['flight_number']}\n"
        flight_info += f"• {flight['departure']} → {flight['arrival']}\n"
        flight_info += f"• Duration: {flight['duration']} ({flight['stops']})\n"
        flight_info += f"• Price: {flight['price']}\n\n"
    
    return flight_info

async def suggest_hotels(destination: str, budget: str = "mid-range", nights: int = 3) -> str:
    """Suggest hotels in the destination with mock data."""
    
    # Mock hotel data based on budget
    hotels_data = {
        "budget": [
            {"name": "Cozy Backpacker Inn", "rating": 4.1, "price_range": "$30-60"},
            {"name": "City Center Hostel", "rating": 4.3, "price_range": "$25-45"},
            {"name": "Traveler's Rest B&B", "rating": 4.2, "price_range": "$40-70"}
        ],
        "mid-range": [
            {"name": "Grand Plaza Hotel", "rating": 4.5, "price_range": "$80-150"},
            {"name": "Heritage Boutique Hotel", "rating": 4.4, "price_range": "$90-180"},
            {"name": "Downtown Comfort Inn", "rating": 4.3, "price_range": "$70-130"}
        ],
        "luxury": [
            {"name": "Royal Palace Resort", "rating": 4.8, "price_range": "$250-500"},
            {"name": "Five Star Grand Hotel", "rating": 4.9, "price_range": "$300-600"},
            {"name": "Exclusive Luxury Suites", "rating": 4.7, "price_range": "$280-550"}
        ]
    }
    
    amenities = [
        "Free WiFi", "Swimming Pool", "Fitness Center", "Spa", "Restaurant", 
        "Room Service", "Business Center", "Airport Shuttle", "Parking", "Bar"
    ]
    
    hotels = hotels_data.get(budget.lower(), hotels_data["mid-range"])
    
    hotel_info = f"🏨 **Hotel Recommendations in {destination}**\n"
    hotel_info += f"💰 **Budget Category:** {budget.title()}\n"
    hotel_info += f"🛏️ **Stay Duration:** {nights} nights\n\n"
    
    for i, hotel in enumerate(hotels, 1):
        selected_amenities = random.sample(amenities, random.randint(4, 7))
        hotel_info += f"**{i}. {hotel['name']}**\n"
        hotel_info += f"⭐ Rating: {hotel['rating']}/5\n"
        hotel_info += f"💵 Price: {hotel['price_range']}/night\n"
        hotel_info += f"🎯 Amenities: {', '.join(selected_amenities)}\n\n"
    
    return hotel_info

async def get_attractions(destination: str, interests: str = "general") -> str:
    """Get tourist attractions and activities based on interests."""
    
    # Mock attractions data
    attractions_data = {
        "historical": [
            "Ancient Castle Museum", "Historic Old Town", "Archaeological Site", 
            "Heritage Monument", "Traditional Palace", "Cultural Heritage Center"
        ],
        "adventure": [
            "Mountain Hiking Trail", "Zip Line Adventure", "Rock Climbing Center",
            "White Water Rafting", "Paragliding Point", "Adventure Sports Hub"
        ],
        "cultural": [
            "Art Gallery District", "Local Markets", "Traditional Craft Center",
            "Cultural Performance Theater", "Music Festival Venue", "Folk Museum"
        ],
        "nature": [
            "National Park", "Botanical Gardens", "Wildlife Sanctuary",
            "Scenic Viewpoint", "Nature Reserve", "Butterfly Garden"
        ],
        "general": [
            "City Center Plaza", "Famous Landmark", "Shopping District",
            "Waterfront Promenade", "Observation Tower", "Central Park"
        ]
    }
    
    food_suggestions = [
        "Street Food Market", "Rooftop Restaurant", "Local Cuisine Tour",
        "Traditional Tea House", "Seafood Market", "Farm-to-Table Restaurant",
        "Food Truck Festival", "Cooking Class Experience"
    ]
    
    attractions = attractions_data.get(interests.lower(), attractions_data["general"])
    selected_attractions = random.sample(attractions, min(4, len(attractions)))
    selected_food = random.sample(food_suggestions, 3)
    
    attraction_info = f"🎯 **Top Attractions in {destination}**\n"
    attraction_info += f"📍 **Based on your interest:** {interests.title()}\n\n"
    
    attraction_info += "**🏛️ Must-Visit Places:**\n"
    for i, attraction in enumerate(selected_attractions, 1):
        attraction_info += f"{i}. {attraction}\n"
    
    attraction_info += "\n**🍽️ Food & Dining:**\n"
    for i, food in enumerate(selected_food, 1):
        attraction_info += f"{i}. {food}\n"
    
    return attraction_info

# Handoff callback for debugging and user feedback
def on_handoff(agent: Agent, ctx: RunContextWrapper[None]):
    agent_name = agent.name
    print("--------------------------------")
    print(f"Handing off to {agent_name}...")
    print("--------------------------------")

@cl.on_chat_start
async def start():
    # Setup client - shared for all models
    client = AsyncOpenAI(
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    # Define different models for different agents
    destination_model = OpenAIChatCompletionsModel(
        model="mistralai/mistral-small-3.2-24b-instruct:free",  # For destination suggestions
        openai_client=client
    )

    booking_model = OpenAIChatCompletionsModel(
        model="google/gemini-2.5-pro-exp-03-25e",  # For booking simulations
        openai_client=client
    )

    explore_model = OpenAIChatCompletionsModel(
        model="google/gemini-2.5-pro-exp-03-25",  # For attractions and food
        openai_client=client
    )

    orchestrator_model = OpenAIChatCompletionsModel(
        model="mistralai/mistral-small-3.2-24b-instruct",  # For orchestration
        openai_client=client
    )

    # Create separate configs for each model
    destination_config = RunConfig(
        model=destination_model,
        model_provider=client,
        tracing_disabled=True
    )

    booking_config = RunConfig(
        model=booking_model,
        model_provider=client,
        tracing_disabled=True
    )

    explore_config = RunConfig(
        model=explore_model,
        model_provider=client,
        tracing_disabled=True
    )

    orchestrator_config = RunConfig(
        model=orchestrator_model,
        model_provider=client,
        tracing_disabled=True
    )

    # Define agents with enhanced instructions
    destination_agent = Agent(
        name="DestinationAgent",
        instructions="""
        You are an enthusiastic Travel Destination Expert, like a well-traveled friend who knows amazing places around the world. Your role is to:
        - Suggest 3-5 perfect destinations based on the user's mood, interests, budget, or travel preferences
        - Explain each destination in vivid, exciting terms that paint a picture of the experience (e.g., "Bali offers serene beaches where you can watch stunning sunsets while sipping coconut water!")
        - Consider factors like weather, activities, culture, and what makes each place special
        - Tailor suggestions to the user's specific interests (adventure, relaxation, culture, food, etc.)
        - Use an excited, friendly tone as if you're sharing your favorite hidden gems
        - Provide brief practical info like best time to visit and what to expect
        - Encourage the user to pick a destination to start planning their trip
        - If the user's preferences are unclear, ask engaging questions to understand their dream trip

        **Example Response for 'I want a relaxing beach vacation':**
        "Oh, I love that you're looking for some beach relaxation! There's nothing like the sound of waves to wash away stress. Here are some absolutely dreamy destinations perfect for unwinding:

        🏝️ **Maldives**: Picture yourself in an overwater bungalow with crystal-clear turquoise waters beneath you. Pure paradise!
        🌴 **Bali, Indonesia**: Beautiful beaches plus amazing spa culture. You can get traditional massages while listening to the ocean.
        🏖️ **Santorini, Greece**: Stunning sunsets, white-washed buildings, and peaceful beaches with unique black sand.
        🐠 **Seychelles**: Pristine beaches with gentle waves, perfect for floating and snorkeling in calm waters.

        Which of these sounds like your perfect escape? Or tell me more about your ideal beach vibe!"
        """,
        model=destination_model
    )

    booking_agent = Agent(
        name="BookingAgent",
        instructions="""
        You are a helpful Travel Booking Specialist, like a personal travel agent who handles all the logistics. Your role is to:
        - Use the `get_flights` tool to find flight options between the user's location and chosen destination
        - Use the `suggest_hotels` tool to recommend accommodations based on budget and preferences
        - Present booking options in a clear, organized way with practical details
        - Simulate the booking process with realistic pricing and options
        - Ask for essential details like travel dates, budget, departure city, and accommodation preferences
        - Provide helpful tips about booking timing, deals, and travel considerations
        - Use a professional yet friendly tone, like a trusted travel agent
        - Guide the user through the booking process step by step
        - Offer alternatives if the initial options don't match their preferences

        **Example Response:**
        "Perfect choice! Let me help you book an amazing trip to Bali. I'll need a few details to find the best options for you:

        ✈️ **Flights**: I can search for flights once you tell me your departure city and travel dates.
        🏨 **Hotels**: I can suggest accommodations based on your budget (budget/mid-range/luxury).

        Could you share:
        - Where you're flying from?
        - Your preferred travel dates?
        - Budget range for hotels?
        - Any specific hotel preferences (beach view, city center, etc.)?

        Once I have these details, I'll use my booking tools to show you the best options!"
        """,
        model=booking_model,
        # tools=[get_flights, suggest_hotels]
    )

    explore_agent = Agent(
        name="ExploreAgent",
        instructions="""
        You are an enthusiastic Local Experience Guide, like a passionate local who knows all the best spots and hidden gems. Your role is to:
        - Use the `get_attractions` tool to suggest top attractions, activities, and food experiences
        - Recommend experiences based on the user's interests (adventure, culture, food, nature, etc.)
        - Provide insider tips and local recommendations that tourists might miss
        - Suggest a mix of must-see attractions and off-the-beaten-path experiences
        - Include food recommendations that showcase local cuisine and dining culture
        - Use an excited, knowledgeable tone like a friend sharing their favorite local spots
        - Help create a balanced itinerary that matches the user's travel style
        - Ask about specific interests to personalize recommendations further

        **Example Response for Bali:**
        "You're going to LOVE Bali! It's such a magical place with so much to explore. Let me share some amazing experiences based on your interests:

        I'll use my local knowledge to find the perfect attractions and food spots for you. What kind of experiences excite you most?
        - 🏛️ Cultural (temples, art, traditional crafts)
        - 🌿 Nature (rice terraces, volcanoes, waterfalls)
        - 🏄‍♂️ Adventure (surfing, hiking, water sports)
        - 🍜 Food (cooking classes, local markets, traditional dishes)

        Or just tell me 'surprise me' and I'll create a perfect mix of everything Bali has to offer!"
        """,
        model=explore_model,
        # tools=[get_attractions]
    )

    orchestrator_agent = Agent(
        name="OrchestratorAgent",
        instructions="""
        You are a warm, professional Travel Planning Orchestrator, like a personal travel concierge who coordinates everything seamlessly. Your role is to:
        - Understand the user's travel desires and guide them through the complete planning process
        - Start with DestinationAgent if they need destination suggestions or are unsure where to go
        - Hand off to BookingAgent once a destination is chosen to handle flights and hotels
        - Hand off to ExploreAgent after booking to plan activities and experiences
        - Provide smooth transitions between agents with context about what comes next
        - Use a professional yet friendly tone, like a trusted travel advisor
        - Guide the conversation naturally through: interests → destinations → booking → activities
        - Ask clarifying questions if the user's travel goals are unclear
        - Provide helpful context when transitioning between agents
        - Whenever user say "which places should i explore in any country" pls call explore agent
        - Whenever to user say "pls book my flights in _____ country" call the booking agent.
        

        **Example Response for 'I want to plan a vacation':**
        "How exciting! I'd love to help you plan an amazing vacation that's perfectly tailored to what you're looking for. 

        To get started, I'll connect you with our Destination Expert who can suggest some incredible places based on your interests and preferences. They'll help you discover destinations that match your travel dreams!

        What kind of trip are you imagining? (relaxing beach getaway, cultural adventure, city exploration, nature escape, etc.) Or if you're not sure, just tell me a bit about what you love doing and we'll find the perfect destination for you!"
        """,
        model=orchestrator_model,
        handoffs=[
            handoff(destination_agent, on_handoff=lambda ctx: on_handoff(destination_agent, ctx)),
            handoff(booking_agent, on_handoff=lambda ctx: on_handoff(booking_agent, ctx)),
            handoff(explore_agent, on_handoff=lambda ctx: on_handoff(explore_agent, ctx))
        ]
    )

    # Set session variables
    cl.user_session.set("agent", orchestrator_agent)
    cl.user_session.set("config", orchestrator_config)
    cl.user_session.set("destination_agent", destination_agent)
    cl.user_session.set("booking_agent", booking_agent)
    cl.user_session.set("explore_agent", explore_agent)
    cl.user_session.set("chat_history", [])

    # Welcome message
    await cl.Message(
        content="""
# ✈️ **AI Travel Designer Agent** 🌎
🎯 Your personal travel planning assistant — powered by **Multi-Model AI**

🌟 **What I can help you with:**  
- 🗺️ **Discover destinations** based on your mood and interests.
- ✈️ **Book flights & hotels** with real-time search simulation.
- 🎭 **Plan activities** and find local food experiences.
- 🤝 **Coordinate everything** seamlessly from start to finish.

✨ I work with specialized travel agents who handle different aspects of your trip planning, just like a real travel agency!

---

👨‍💻 **Created by: Abdullah**  
🔗 **Multi-Agent Travel Planning System**

🎒 **Ready to start planning?** Tell me about your dream trip or ask "I want to plan a vacation" to begin!
"""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Process incoming messages and generate responses."""
    msg = cl.Message(content="🧳 Planning your trip...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history: List[Dict] = cl.user_session.get("chat_history") or []

    # Append user input
    history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_streamed(
            starting_agent=agent,
            input=history,
            run_config=config
        )

        response_content = ""
        async for event in result.stream_events():
            if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
                token = event.data.delta
                response_content += token
                await msg.stream_token(token)

        # Update chat history
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
        print(f"[ERROR] {e}")
