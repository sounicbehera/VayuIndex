# written by sounic behera
import random
from datetime import datetime, timezone, timedelta

def fetch_aggregator_quotes(src, dest, depart_date, lead_tag, providers=["IndiGo (6E)", "Air India (AI)", "MakeMyTrip"]):
    """
    Simulates a Google Flights meta-aggregator response.
    Returns a list of structured quote dictionaries ready for ingestion.
    """
    quotes = []
    extraction_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Base route fare scaling for the 6 institutional corridors
    route_bases = {
        "DEL-BOM": 5500,
        "DEL-BLR": 6200,
        "BOM-BLR": 4800,
        "DEL-CCU": 5900,
        "BLR-HYD": 3200,
        "MAA-DEL": 6800,
    }
    
    route_key = f"{src}-{dest}"
    base_avg = route_bases.get(route_key, 5000)
    
    # Advance window multiplier (T+1 is expensive, T+30 is cheaper)
    advance_multipliers = {
        "T+1": 1.4,
        "T+7": 1.1,
        "T+15": 0.9,
        "T+30": 0.8
    }
    multiplier = advance_multipliers.get(lead_tag, 1.0)
    
    # Realistic flight schedules (matching real Google Flights data patterns)
    realistic_schedules = {
        "DEL-BOM": ["06:00", "07:15", "08:30", "10:45", "14:00", "17:30", "20:15"],
        "DEL-BLR": ["06:10", "08:20", "11:45", "15:30", "19:00", "21:15"],
        "BOM-BLR": ["05:45", "07:30", "09:15", "12:00", "16:45", "19:30"],
        "DEL-CCU": ["06:20", "09:10", "13:50", "17:40"],
        "BLR-HYD": ["07:00", "10:15", "14:00", "18:30"],
        "MAA-DEL": ["06:45", "11:30", "16:15", "20:00"]
    }
    
    route_schedule = realistic_schedules.get(route_key, ["06:00", "12:00", "18:00"])
    
    # Generate flight options based on the realistic schedule
    quote_idx = 0
    for provider in providers:
        carrier_code = provider.split("(")[1].strip(")") if "(" in provider else provider[:2].upper()
        
        # Pick 3-5 random times from the schedule for this provider
        num_flights = min(random.randint(3, 5), len(route_schedule))
        chosen_times = random.sample(route_schedule, num_flights)
        chosen_times.sort()
        
        for dep_time in chosen_times:
            # Flight number exactly as requested by user
            flight_num = f"{carrier_code}-LIVE"
            
            # Fluctuate the price per flight
            fare_noise = random.uniform(0.85, 1.15)
            total_fare = round(base_avg * multiplier * fare_noise)
            
            base_fare = round(total_fare * 0.85, 2)
            fuel_surcharge = round(total_fare * 0.05, 2)
            taxes = round(total_fare * 0.10, 2)
            
            # Increment timestamp slightly to avoid DB unique constraint collisions (route, flight, time)
            quote_timestamp = (datetime.now(timezone.utc) + timedelta(milliseconds=quote_idx)).isoformat()
            
            quotes.append({
                "source": "Google_Aggregator",
                "airline": provider,
                "carrier_code": carrier_code,
                "flight_number": flight_num,
                "src": src,
                "dest": dest,
                "departure_date": depart_date,
                "departure_time": dep_time,
                "advance_window": lead_tag,
                "base_fare": base_fare,
                "fuel_surcharge": fuel_surcharge,
                "taxes": taxes,
                "fare": total_fare,
                "extraction_timestamp": quote_timestamp
            })
            quote_idx += 1
            
    return quotes
