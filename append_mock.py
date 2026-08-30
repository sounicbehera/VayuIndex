import xml.etree.ElementTree as ET
from fastapi import Request, Response
import random

ROUTE_FLIGHT_MAP = {
    "DEL-BOM": "5271",
    "DEL-BLR": "2131",
    "BOM-BLR": "5262",
    "DEL-CCU": "2022",
    "DEL-MAA": "2568"
}

def append_to_main():
    with open('api/app/main.py', 'a') as f:
        f.write('''
import xml.etree.ElementTree as ET
from fastapi import Request, Response
import random

ROUTE_FLIGHT_MAP = {
    "DEL-BOM": "5271",
    "DEL-BLR": "2131",
    "BOM-BLR": "5262",
    "DEL-CCU": "2022",
    "DEL-MAA": "2568"
}

@app.post("/mock/ndc/v21.3/AirShopping", tags=["Mock NDC API"])
async def mock_ndc_air_shopping(request: Request):
    """
    Simulates the real IndiGo NDC API for the hackathon by parsing the request
    and returning the exact realistic IATA_AirShoppingRS schema provided.
    """
    body = await request.body()
    try:
        root = ET.fromstring(body)
        ns = {'cmn': 'http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes'}
        origin = root.find('.//cmn:OriginDepCriteria/cmn:IATA_LocationCode', ns).text
        dest = root.find('.//cmn:DestArrivalCriteria/cmn:IATA_LocationCode', ns).text
        date_str = root.find('.//cmn:OriginDepCriteria/cmn:Date', ns).text
    except Exception:
        origin, dest, date_str = "AGX", "COK", "2025-10-19"
        
    flight_num = ROUTE_FLIGHT_MAP.get(f"{origin}-{dest}", str(random.randint(100, 999)))
    
    base_fare = 4500.0 if origin == "DEL" else 5500.0
    tax = base_fare * 0.18
    total = base_fare + tax
    
    fake_hour = random.randint(5, 22)
    fake_min = random.choice(["00", "15", "30", "45"])
    
    xml_response = f"""<IATA_AirShoppingRS xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage">
    <Response>
        <DataLists xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
            <DatedMarketingSegmentList>
                <DatedMarketingSegment>
                    <Arrival>
                        <AircraftScheduledDateTime>{date_str}T23:30:00</AircraftScheduledDateTime>
                        <IATA_LocationCode>{dest}</IATA_LocationCode>
                    </Arrival>
                    <CarrierDesigCode>6E</CarrierDesigCode>
                    <DatedMarketingSegmentId>Mkt-seg0349235905</DatedMarketingSegmentId>
                    <DatedOperatingSegmentRefId>Opr-seg0349235905</DatedOperatingSegmentRefId>
                    <Dep>
                        <AircraftScheduledDateTime>{date_str}T{fake_hour:02d}:{fake_min}:00</AircraftScheduledDateTime>
                        <IATA_LocationCode>{origin}</IATA_LocationCode>
                    </Dep>
                    <MarketingCarrierFlightNumberText>{flight_num}</MarketingCarrierFlightNumberText>
                </DatedMarketingSegment>
            </DatedMarketingSegmentList>
            <PaxList>
                <Pax>
                    <PaxID>ADT0</PaxID>
                    <PTC>ADT</PTC>
                </Pax>
            </PaxList>
            <PaxSegmentList>
                <PaxSegment>
                    <CabinTypeAssociationChoice>
                        <SegmentCabinType>
                            <CabinTypeCode>5</CabinTypeCode>
                            <CabinTypeName>Economy</CabinTypeName>
                        </SegmentCabinType>
                    </CabinTypeAssociationChoice>
                    <DatedMarketingSegmentRefId>Mkt-seg0349235905</DatedMarketingSegmentRefId>
                    <PaxSegmentID>seg0349235905</PaxSegmentID>
                </PaxSegment>
            </PaxSegmentList>
        </DataLists>
        <OffersGroup xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
            <CarrierOffers>
                <Offer>
                    <OfferID>654432311_id-542b4719-dc51-4b40-a92a-8b213ae785b9-o-1</OfferID>
                    <OfferItem>
                        <FareDetail>
                            <FareComponent>
                                <CabinType>
                                    <CabinTypeCode>5</CabinTypeCode>
                                    <CabinTypeName>Economy</CabinTypeName>
                                </CabinType>
                                <FareBasisCode>C0IP</FareBasisCode>
                                <PaxSegmentRefID>seg0349235905</PaxSegmentRefID>
                            </FareComponent>
                            <PaxRefID>ADT0</PaxRefID>
                            <Price>
                                <BaseAmount CurCode="INR">{base_fare:.2f}</BaseAmount>
                                <TaxSummary>
                                    <Tax>
                                        <Amount CurCode="INR">{tax:.2f}</Amount>
                                    </Tax>
                                    <TotalTaxAmount CurCode="INR">{tax:.2f}</TotalTaxAmount>
                                </TaxSummary>
                                <TotalAmount CurCode="INR">{total:.2f}</TotalAmount>
                            </Price>
                        </FareDetail>
                        <MandatoryInd>true</MandatoryInd>
                        <OfferItemID>654432311_id-542b4719-dc51-4b40-a92a-8b213ae785b9-o-1-1</OfferItemID>
                        <Price>
                            <BaseAmount CurCode="INR">{base_fare:.2f}</BaseAmount>
                            <TaxSummary>
                                <Tax>
                                    <Amount CurCode="INR">{tax:.2f}</Amount>
                                </Tax>
                                <TotalTaxAmount CurCode="INR">{tax:.2f}</TotalTaxAmount>
                            </TaxSummary>
                            <TotalAmount CurCode="INR">{total:.2f}</TotalAmount>
                        </Price>
                    </OfferItem>
                </Offer>
            </CarrierOffers>
        </OffersGroup>
    </Response>
</IATA_AirShoppingRS>"""
    return Response(content=xml_response, media_type="application/xml")
''')

if __name__ == '__main__':
    append_to_main()
