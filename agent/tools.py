from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from agent.db import get_connection


class SearchInput(BaseModel):
    location: str = Field(..., description="Bangladesh location, e.g. Cox's Bazar")
    guests: int = Field(..., ge=1)
    max_price: Optional[int] = None


class ListingInput(BaseModel):
    listing_id: int


class BookingInput(BaseModel):
    listing_id: int
    guest_name: str = "Guest"
    guests: int
    check_in: str
    check_out: str


@tool(args_schema=SearchInput)
def search_available_properties(location: str, guests: int, max_price: Optional[int] = None) -> list[dict]:
    """Search available properties by location, guest count, and optional max BDT price."""
    query = """
        SELECT id, name, location, price_per_night, max_guests, description, amenities
        FROM listings
        WHERE LOWER(location) LIKE LOWER(%s)
          AND max_guests >= %s
    """
    params: list = [f"%{location}%", guests]

    if max_price:
        query += " AND price_per_night <= %s"
        params.append(max_price)

    query += " ORDER BY price_per_night ASC LIMIT 5"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()


@tool(args_schema=ListingInput)
def get_listing_details(listing_id: int) -> dict:
    """Get full details for one listing."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, location, price_per_night, max_guests, description, amenities
                FROM listings
                WHERE id = %s
                """,
                (listing_id,),
            )
            row = cur.fetchone()
            return row or {"error": "Listing not found"}


@tool(args_schema=BookingInput)
def create_booking(
    listing_id: int,
    guest_name: str,
    guests: int,
    check_in: str,
    check_out: str,
) -> dict:
    """Create a booking for a listing."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookings (listing_id, guest_name, guests, check_in, check_out, status)
                VALUES (%s, %s, %s, %s, %s, 'confirmed')
                RETURNING id, listing_id, guest_name, guests, check_in, check_out, status
                """,
                (listing_id, guest_name, guests, check_in, check_out),
            )
            booking = cur.fetchone()
            conn.commit()

    return booking