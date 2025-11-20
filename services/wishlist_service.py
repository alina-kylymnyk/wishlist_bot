from typing import List, Optional
from database import (
    add_wish as db_add_wish,
    get_user_wishes as db_get_user_wishes,
    get_wish as db_get_wish,
    delete_wish as db_delete_wish,
    update_wish as db_update_wish
)
from models import Wish

class WishlistService:
    """Service layer for wishlist operations"""

    MAX_WISHES_PER_USER = 100
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 100

    def __init__(self):
        self.cache = {}

    
    # ===== BUSINESS LOGIC =====

    def can_add_wish(self, user_id: int) -> bool:
        """Check if user can add more wishes"""
        current_wishes = self.get_user_wishes(user_id)
        return len(current_wishes) < self.MAX_WISHES_PER_USER
    
    def validate_title(self, title: str) -> tuple[bool, Optional[str]]:
        """
        Validate wish title
        Returns: (is_valid, error_message)
        """
        if not title or len(title.strip()) < self.MIN_TITLE_LENGTH:
            return False, f"Title too short (min {self.MIN_TITLE_LENGTH} chars)"
        
        if len(title)> self.MAX_TITLE_LENGTH:
            return False, f"Title too long (max {self.MAX_TITLE_LENGTH} chars)"
        
        return True, None
    
    def validate_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Validate URL format"""
        if not url:
            return True, None # URL optional
        
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        return True, None
    
    # ===== CRUD OPERATIONS (with logic) =====

    def add_wish(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        price: Optional[str] = None,
        image_file_id: Optional[str] = None
    ) -> tuple[Optional[Wish], Optional[str]]:
        """
        Add a new wish with validation
        Returns: (wish, error_message)
        """
        # Limit check
        if not self.can_add_wish(user_id):
            return None, f"You've reached the limit of {self.MAX_WISHES_PER_USER} wishes"
        
        # Title validation
        is_valid, error = self.validate_title(title)
        if not is_valid: 
            return None, error
        
        # URL validation 
        is_valid, error = self.validate_url(url)
        if not is_valid:
            return None, error
        
        # Save to db
        wish = db_add_wish(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            url=url,
            price=price,
            image_file_id=image_file_id
        )

        if user_id in self.cache:
            del self.cache[user_id]

        return wish, None


    def get_user_wishes(self, user_id: int) -> List[Wish]:
        """Get all wishes for a user (with caching)"""
        # Check cache
        if user_id in self.cache:
            return self.cache[user_id]
        
        # Get from db
        wishes = db_get_user_wishes(user_id)

        # Save to cache
        self.cache[user_id] = wishes

        return wishes
    
    def get_wish(self, wish_id: int, user_id: int) -> Optional[Wish]:
        """
        Get a wish by ID with ownership check
        Returns None if wish doesn't exist or doesn't belong to user
        """
        wish = db_get_wish(wish_id)

        if not wish:
            return None
        
        # Owner verification
        if wish.user_id != user_id:
            return None
        
        return wish
    
    def update_wish(
        self,
        wish_id: int,
        user_id: int,
        **updates
    )-> tuple[Optional[Wish], Optional[str]]:
        """
        Update wish with validation
        Returns: (updated_wish, error_message)
        """
        # Check existence and owner
        wish = self.get_wish(wish_id, user_id)
        if not wish:
            return None, "Wish not found or access denied"
        
        # Validate title if updated
        if 'title' in updates:
            is_valid, error = self.validate_url(updates['title'])
            if not is_valid:
                return None, error
            
        #  Validate URL if updated 
        if 'url' in updates:
            is_valid, error = self.validate_url(updates['url'])
            if not is_valid:
                return None, error
            
        # Update db
        updated_wish = db_update_wish(wish_id, user_id, **updates)

        # Disable cache
        if user_id in self.cache:
            del self.cache[user_id]

        return updated_wish, None
    
    def delete_wish(self, wish_id: int, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Delete wish with ownership check
        Returns: (success, error_message)
        """
        # Check existence and owner
        wish = self.get_wish(wish_id, user_id)
        if not wish:
            return False, "Wish not found or access denied"
        
        # Delete from db 
        success = db_delete_wish(wish_id, user_id)

        # Disable cache
        if user_id in self.cache:
            del self.cache[user_id]

        return success, None if success else "Failed to delete"

# Global instance (singleton)
wishlist_service = WishlistService()



        












                