# written by sounic behera
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from celery import Celery
from storage.orchestrator import StorageOrchestrator


def fetch_indigo_ndc(origin, destination, travel_date):
    # We use the official IATA NDC payload, dynamically injecting your route variables.
    payload = f"""<IATA_AirShoppingRQ xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage">
       <DistributionChain>
          <DistributionChainLink xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <Ordinal>1</Ordinal>
             <OrgRole>Seller</OrgRole>
             <ParticipatingOrg>
                <Name>6E Travel</Name>
                <OrgID>TESTAPI</OrgID>
             </ParticipatingOrg>
          </DistributionChainLink>
       </DistributionChain>
       <PayloadAttributes>
          <VersionNumber xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">21.3</VersionNumber>
       </PayloadAttributes>
       <POS>
          <Country xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <CountryCode>IN</CountryCode>
             <CountryName>India</CountryName>
          </Country>
       </POS>
       <Request>
          <FlightRequest xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <FlightRequestOriginDestinationsCriteria>
                <OriginDestCriteria>
                    <DestArrivalCriteria>
                        <IATA_LocationCode>{destination}</IATA_LocationCode>
                    </DestArrivalCriteria>
                    <OriginDepCriteria>
                        <Date>{travel_date}</Date>
                        <IATA_LocationCode>{origin}</IATA_LocationCode>
                    </OriginDepCriteria>
                </OriginDestCriteria>
             </FlightRequestOriginDestinationsCriteria>
          </FlightRequest>
          <PaxList xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
                <Pax>
                    <PaxID>ADT0</PaxID>
                    <PTC>ADT</PTC>
                </Pax>
          </PaxList>
          <ResponseParameters xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <CurParameter>
                <CurCode>INR</CurCode>
             </CurParameter>
          </ResponseParameters>
       </Request>
    </IATA_AirShoppingRQ>"""

    headers = {
        "Content-Type": "Application/Xml; Charset=Utf-8",
        "Ocp-Apim-Subscription-Key": "YOUR_API_KEY"
    }

    # Point it to your local FastAPI mock route:
    url = "http://vayu_api:8000/mock/ndc/v21.3/AirShopping"

    try:
        import time, random
        # Apply random simulation jitter
        time.sleep(random.uniform(0.1, 1.0))
        
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request failed for {origin}-{destination}: {e}")
        return None
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery('vayu_scraper', broker=REDIS_URL)

@app.task(bind=True, name='scraper.worker.scrape_flight_corridor', max_retries=3, default_retry_delay=60)
def scrape_flight_corridor(self, provider: str, src: str, dest: str, depart_date: str, lead_tag: str):
    """
    Celery worker task that invokes XML NDC API for IndiGo and persists results.
    """
    payload = f"""<IATA_AirShoppingRQ xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage">
       <DistributionChain>
          <DistributionChainLink xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <Ordinal>1</Ordinal>
             <OrgRole>Seller</OrgRole>
             <ParticipatingOrg>
                <Name>6E Travel</Name>
                <OrgID>TESTAPI</OrgID>
             </ParticipatingOrg>
          </DistributionChainLink>
       </DistributionChain>
       <POS>
          <Country xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <CountryCode>IN</CountryCode>
             <CountryName>India</CountryName>
          </Country>
       </POS>
       <Request>
          <FlightRequest xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <FlightRequestOriginDestinationsCriteria>
                <OriginDestCriteria>
                    <DestArrivalCriteria>
                        <IATA_LocationCode>{dest}</IATA_LocationCode>
                    </DestArrivalCriteria>
                    <OriginDepCriteria>
                        <Date>{depart_date}</Date>
                        <IATA_LocationCode>{src}</IATA_LocationCode>
                    </OriginDepCriteria>
                </OriginDestCriteria>
             </FlightRequestOriginDestinationsCriteria>
          </FlightRequest>
          <PaxList xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
                <Pax>
                    <PaxID>ADT0</PaxID>
                    <PTC>ADT</PTC>
                </Pax>
          </PaxList>
          <ResponseParameters xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
             <CurParameter>
                <CurCode>INR</CurCode>
             </CurParameter>
          </ResponseParameters>
       </Request>
    </IATA_AirShoppingRQ>"""
    
    headers = {
        "Content-Type": "Application/Xml; Charset=Utf-8",
        "Ocp-Apim-Subscription-Key": "YOUR_API_KEY"
    }
    
    url = "http://vayu_api:8000/mock/ndc/v21.3/AirShopping"
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        xml_text = response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API Request failed for {src}-{dest}: {e}")
        raise self.retry(exc=e)

    try:
        root = ET.fromstring(xml_text)
        ns = {
            'msg': 'http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage',
            'cmn': 'http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes'
        }
        
        segments = root.findall('.//cmn:DatedMarketingSegment', ns)
        offers = root.findall('.//cmn:OfferItem', ns)
        
        quotes = []
        extraction_timestamp = datetime.now(timezone.utc).isoformat()
        
        for seg, offer in zip(segments, offers):
            flight_num = seg.find('cmn:MarketingCarrierFlightNumberText', ns).text
            dep_time_raw = seg.find('cmn:Dep/cmn:AircraftScheduledDateTime', ns).text
            dep_time = dep_time_raw.split('T')[1][:8] if 'T' in dep_time_raw else dep_time_raw
            
            total_fare = float(offer.find('.//cmn:TotalAmount', ns).text)
            
            quotes.append({
                "source": "IndiGo_NDC",
                "airline": "IndiGo",
                "carrier_code": "6E",
                "flight_number": f"6E-{flight_num}",
                "src": src,
                "dest": dest,
                "departure_date": depart_date,
                "departure_time": dep_time,
                "advance_window": lead_tag,
                "base_fare": total_fare * 0.85,
                "fuel_surcharge": total_fare * 0.05,
                "taxes": total_fare * 0.10,
                "fare": total_fare,
                "extraction_timestamp": extraction_timestamp
            })
            
            print(f"[OK] Parsed 6E-{flight_num} at {dep_time} for Rs. {total_fare}")
            
        if quotes:
            # O(1) Idempotent Insert to TimescaleDB
            result_msg = StorageOrchestrator.persist_quotes(quotes)
            return {"status": "success", "message": result_msg, "extracted": len(quotes)}
        else:
            return {"status": "failed", "message": "No quotes extracted", "extracted": 0}
            
    except Exception as exc:
        print(f"Error parsing NDC response for {src}-{dest}: {exc}")
        raise self.retry(exc=exc)