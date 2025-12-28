"""Idea management endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

from api.models.idea import IdeaCreate, IdeaResponse, IdeaUpdate
from storage.ideas_storage import IdeasStorage

router = APIRouter(prefix="/api/ideas", tags=["Ideas"])

# Storage instance
_ideas_storage = IdeasStorage()


@router.post("", response_model=IdeaResponse, status_code=201)
async def create_idea(idea: IdeaCreate):
    """
    Create a new video idea.
    
    Ideas can be used multiple times to generate different videos
    based on the same concept.
    
    Args:
        idea: Idea creation request with title, description, and tags
        
    Returns:
        Created idea with generated ID and timestamps
    """
    created_idea = _ideas_storage.create(
        title=idea.title,
        description=idea.description,
        tags=idea.tags
    )
    
    return IdeaResponse(**created_idea)


@router.get("", response_model=List[IdeaResponse])
async def list_ideas():
    """
    List all saved video ideas.
    
    Returns ideas sorted by creation date (newest first).
    
    Returns:
        List of all ideas with their metadata
    """
    ideas = _ideas_storage.list_all()
    return [IdeaResponse(**idea) for idea in ideas]


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(idea_id: str):
    """
    Get a specific idea by ID.
    
    Args:
        idea_id: Idea identifier
        
    Returns:
        Idea details
    """
    idea = _ideas_storage.get(idea_id)
    
    if not idea:
        raise HTTPException(
            status_code=404,
            detail=f"Idea with id {idea_id} not found"
        )
    
    return IdeaResponse(**idea)


@router.patch("/{idea_id}", response_model=IdeaResponse)
async def update_idea(idea_id: str, update: IdeaUpdate):
    """
    Update an existing idea.
    
    Only provided fields will be updated.
    
    Args:
        idea_id: Idea identifier
        update: Fields to update
        
    Returns:
        Updated idea
    """
    updated_idea = _ideas_storage.update(
        idea_id=idea_id,
        title=update.title,
        description=update.description,
        tags=update.tags
    )
    
    if not updated_idea:
        raise HTTPException(
            status_code=404,
            detail=f"Idea with id {idea_id} not found"
        )
    
    return IdeaResponse(**updated_idea)


@router.delete("/{idea_id}")
async def delete_idea(idea_id: str):
    """
    Delete an idea.
    
    Args:
        idea_id: Idea identifier
        
    Returns:
        Success message
    """
    deleted = _ideas_storage.delete(idea_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Idea with id {idea_id} not found"
        )
    
    return {
        "message": f"Idea {idea_id} deleted successfully"
    }


@router.get("/random/pick", response_model=IdeaResponse)
async def get_random_idea():
    """
    Get a random idea for automated generation.
    
    Useful for scheduler to pick diverse content.
    
    Returns:
        Random idea from storage
    """
    idea = _ideas_storage.get_random()
    
    if not idea:
        raise HTTPException(
            status_code=404,
            detail="No ideas available. Create some ideas first."
        )
    
    return IdeaResponse(**idea)
