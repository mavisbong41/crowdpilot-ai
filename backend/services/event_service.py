from models.event import EventCreate, EventResponse, EventUpdate
from services.base import CRUDService


class EventService(CRUDService[EventCreate, EventUpdate, EventResponse]):
    collection_name = "events"
    response_model = EventResponse
