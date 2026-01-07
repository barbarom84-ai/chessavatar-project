"""
Avatar Manager - Storage and management of AI avatars
"""
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict
from datetime import datetime
from core.style_analyzer import PlayerStyle


@dataclass
class Avatar:
    """Data structure for an AI Avatar"""
    id: str
    username: str
    platform: str  # 'lichess' or 'chesscom' or 'chessmaster'
    display_name: str
    photo_path: Optional[str]
    created_date: str
    last_played: Optional[str]
    games_played: int
    
    # Player style data (for online players) or Chessmaster personality
    style_data: Dict
    
    # Chessmaster personality name (if platform is 'chessmaster')
    chessmaster_personality: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
        
    @staticmethod
    def from_dict(data: Dict) -> 'Avatar':
        """Create from dictionary"""
        return Avatar(**data)


class AvatarManager:
    """Manager for AI avatars with persistent storage"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.avatars_file = self.config_dir / "avatars_config.json"
        self.avatars_dir = self.config_dir / "avatars"
        self.avatars_dir.mkdir(exist_ok=True)
        
        # Photos directory
        self.photos_dir = self.avatars_dir / "photos"
        self.photos_dir.mkdir(exist_ok=True)
        
        # Cache directory for games
        self.cache_dir = self.avatars_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        self.avatars: List[Avatar] = []
        self.load_avatars()
        
    def create_avatar(
        self,
        username: str,
        platform: str,
        player_style: Optional[PlayerStyle] = None,
        display_name: Optional[str] = None,
        photo_path: Optional[str] = None,
        chessmaster_personality: Optional[str] = None
    ) -> Avatar:
        """
        Create a new avatar
        
        Args:
            username: Player's username
            platform: Platform (lichess/chesscom/chessmaster)
            player_style: Analyzed player style (for online players)
            display_name: Custom display name
            photo_path: Path to profile photo
            chessmaster_personality: Personality name (for Chessmaster avatars)
            
        Returns:
            Created Avatar object
        """
        # Generate unique ID
        avatar_id = self._generate_id(username, platform)
        
        # Copy photo if provided
        avatar_photo_path = None
        if photo_path and Path(photo_path).exists():
            avatar_photo_path = self._save_photo(avatar_id, photo_path)
        
        # Style data - either from player analysis or empty for Chessmaster
        style_data = {}
        if player_style:
            style_data = self._style_to_dict(player_style)
        elif platform == 'chessmaster' and not chessmaster_personality:
            # Default personality if none specified
            chessmaster_personality = "Default"
            
        # Create avatar
        avatar = Avatar(
            id=avatar_id,
            username=username,
            platform=platform,
            display_name=display_name or username,
            photo_path=avatar_photo_path,
            created_date=datetime.now().isoformat(),
            last_played=None,
            games_played=0,
            style_data=style_data,
            chessmaster_personality=chessmaster_personality
        )
        
        self.avatars.append(avatar)
        self.save_avatars()
        
        return avatar
        
    def update_avatar(
        self,
        avatar_id: str,
        display_name: Optional[str] = None,
        photo_path: Optional[str] = None,
        chessmaster_personality: Optional[str] = None
    ) -> bool:
        """
        Update an existing avatar
        
        Args:
            avatar_id: Avatar ID
            display_name: New display name
            photo_path: New photo path
            chessmaster_personality: New Chessmaster personality name
            
        Returns:
            True if successful
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar:
            return False
            
        if display_name:
            avatar.display_name = display_name
            
        if photo_path and Path(photo_path).exists():
            # Delete old photo
            if avatar.photo_path and Path(avatar.photo_path).exists():
                try:
                    Path(avatar.photo_path).unlink()
                except:
                    pass
            # Save new photo
            avatar.photo_path = self._save_photo(avatar_id, photo_path)
        
        if chessmaster_personality and avatar.platform == 'chessmaster':
            avatar.chessmaster_personality = chessmaster_personality
            
        self.save_avatars()
        return True
        
    def delete_avatar(self, avatar_id: str) -> bool:
        """
        Delete an avatar
        
        Args:
            avatar_id: Avatar ID
            
        Returns:
            True if successful
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar:
            return False
            
        # Delete photo
        if avatar.photo_path and Path(avatar.photo_path).exists():
            try:
                Path(avatar.photo_path).unlink()
            except:
                pass
                
        # Remove from list
        self.avatars = [a for a in self.avatars if a.id != avatar_id]
        self.save_avatars()
        
        return True
        
    def get_avatar(self, avatar_id: str) -> Optional[Avatar]:
        """Get avatar by ID"""
        for avatar in self.avatars:
            if avatar.id == avatar_id:
                return avatar
        return None
        
    def get_all_avatars(self) -> List[Avatar]:
        """Get all avatars"""
        return self.avatars.copy()
        
    def record_game_played(self, avatar_id: str):
        """Record that a game was played against an avatar"""
        avatar = self.get_avatar(avatar_id)
        if avatar:
            avatar.games_played += 1
            avatar.last_played = datetime.now().isoformat()
            self.save_avatars()
            
    def get_player_style(self, avatar_id: str) -> Optional[PlayerStyle]:
        """
        Get PlayerStyle object from avatar
        
        Args:
            avatar_id: Avatar ID
            
        Returns:
            PlayerStyle object or None (Chessmaster avatars return None)
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar:
            return None
        
        # Chessmaster avatars don't have player style
        if avatar.platform == 'chessmaster':
            return None
            
        return self._dict_to_style(avatar.style_data)
    
    def get_chessmaster_personality(self, avatar_id: str) -> Optional[str]:
        """
        Get Chessmaster personality name from avatar
        
        Args:
            avatar_id: Avatar ID
            
        Returns:
            Personality name or None
        """
        avatar = self.get_avatar(avatar_id)
        if not avatar or avatar.platform != 'chessmaster':
            return None
        
        return avatar.chessmaster_personality
        
    def _generate_id(self, username: str, platform: str) -> str:
        """Generate unique avatar ID"""
        base_id = f"{platform}_{username}".lower().replace(" ", "_")
        
        # Check if ID exists
        counter = 1
        avatar_id = base_id
        while any(a.id == avatar_id for a in self.avatars):
            avatar_id = f"{base_id}_{counter}"
            counter += 1
            
        return avatar_id
        
    def _save_photo(self, avatar_id: str, source_path: str) -> str:
        """
        Save avatar photo
        
        Args:
            avatar_id: Avatar ID
            source_path: Source photo path
            
        Returns:
            Saved photo path
        """
        source = Path(source_path)
        extension = source.suffix
        destination = self.photos_dir / f"{avatar_id}{extension}"
        
        try:
            shutil.copy2(source, destination)
            return str(destination)
        except Exception as e:
            print(f"Error saving photo: {e}")
            return None
            
    def _style_to_dict(self, style: PlayerStyle) -> Dict:
        """Convert PlayerStyle to dictionary"""
        return {
            'username': style.username,
            'platform': style.platform,
            'total_games': style.total_games,
            'win_rate': style.win_rate,
            'draw_rate': style.draw_rate,
            'loss_rate': style.loss_rate,
            'average_elo': style.average_elo,
            'top_openings_white': style.top_openings_white,
            'top_openings_black': style.top_openings_black,
            'average_game_length': style.average_game_length,
            'aggressive_score': style.aggressive_score,
            'tactical_score': style.tactical_score,
            'positional_score': style.positional_score,
            'white_win_rate': style.white_win_rate,
            'black_win_rate': style.black_win_rate,
            'preferred_time_control': style.preferred_time_control,
            'estimated_skill_level': style.estimated_skill_level
        }
        
    def _dict_to_style(self, data: Dict) -> PlayerStyle:
        """Convert dictionary to PlayerStyle"""
        # Filter out keys that are not part of PlayerStyle dataclass
        # Get valid fields from PlayerStyle
        from dataclasses import fields
        valid_fields = {f.name for f in fields(PlayerStyle)}
        
        # Filter data to only include valid fields
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return PlayerStyle(**filtered_data)
        
    def save_avatars(self):
        """Save avatars to JSON file"""
        try:
            data = {
                'avatars': [avatar.to_dict() for avatar in self.avatars]
            }
            with open(self.avatars_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving avatars: {e}")
            return False
            
    def load_avatars(self):
        """Load avatars from JSON file"""
        if not self.avatars_file.exists():
            return
            
        try:
            with open(self.avatars_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.avatars = [Avatar.from_dict(a) for a in data.get('avatars', [])]
        except Exception as e:
            print(f"Error loading avatars: {e}")
            self.avatars = []
            
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        total_avatars = len(self.avatars)
        total_games = sum(a.games_played for a in self.avatars)
        
        platforms = {}
        for avatar in self.avatars:
            platforms[avatar.platform] = platforms.get(avatar.platform, 0) + 1
            
        return {
            'total_avatars': total_avatars,
            'total_games': total_games,
            'platforms': platforms
        }

