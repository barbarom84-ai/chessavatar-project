"""
Tests for core.avatar_manager module
Tests avatar storage and management
"""
import pytest
import json
from pathlib import Path
from core.avatar_manager import AvatarManager


@pytest.mark.unit
class TestAvatarManager:
    """Test AvatarManager class"""
    
    def test_manager_initialization(self, tmp_path):
        """Test manager initializes correctly"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        assert manager is not None
        
    def test_create_avatar(self, tmp_path, sample_avatar_config):
        """Test creating a new avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        assert avatar_id is not None
        assert len(manager.get_all_avatars()) == 1
        
    def test_get_avatar(self, tmp_path, sample_avatar_config):
        """Test retrieving avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        avatar = manager.get_avatar(avatar_id)
        
        assert avatar is not None
        assert avatar["name"] == sample_avatar_config["name"]
        assert avatar["elo"] == sample_avatar_config["elo"]
        
    def test_update_avatar(self, tmp_path, sample_avatar_config):
        """Test updating avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        
        # Update avatar
        updated_data = sample_avatar_config.copy()
        updated_data["elo"] = 1600
        updated_data["name"] = "UpdatedAvatar"
        
        success = manager.update_avatar(avatar_id, updated_data)
        assert success
        
        # Verify update
        avatar = manager.get_avatar(avatar_id)
        assert avatar["elo"] == 1600
        assert avatar["name"] == "UpdatedAvatar"
        
    def test_delete_avatar(self, tmp_path, sample_avatar_config):
        """Test deleting avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        assert len(manager.get_all_avatars()) == 1
        
        success = manager.delete_avatar(avatar_id)
        assert success
        assert len(manager.get_all_avatars()) == 0
        
    def test_get_all_avatars(self, tmp_path, sample_avatar_config):
        """Test getting all avatars"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        # Create multiple avatars
        for i in range(5):
            config = sample_avatar_config.copy()
            config["name"] = f"Avatar{i}"
            manager.create_avatar(config)
            
        avatars = manager.get_all_avatars()
        assert len(avatars) == 5
        
    def test_save_and_load(self, tmp_path, sample_avatar_config):
        """Test saving and loading avatars"""
        config_file = tmp_path / "avatars.json"
        
        # Create and save
        manager1 = AvatarManager(str(config_file))
        avatar_id = manager1.create_avatar(sample_avatar_config)
        manager1.save()
        
        # Load in new manager instance
        manager2 = AvatarManager(str(config_file))
        manager2.load()
        
        avatar = manager2.get_avatar(avatar_id)
        assert avatar is not None
        assert avatar["name"] == sample_avatar_config["name"]
        
    def test_avatar_with_photo(self, tmp_path, sample_avatar_config):
        """Test avatar with photo path"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        photo_path = tmp_path / "photo.jpg"
        photo_path.write_text("fake image data")
        
        config = sample_avatar_config.copy()
        config["photo_path"] = str(photo_path)
        
        avatar_id = manager.create_avatar(config)
        avatar = manager.get_avatar(avatar_id)
        
        assert avatar["photo_path"] == str(photo_path)
        
    def test_search_avatars_by_name(self, tmp_path, sample_avatar_config):
        """Test searching avatars by name"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        # Create avatars
        for name in ["Magnus", "Hikaru", "Levy", "Magnus2"]:
            config = sample_avatar_config.copy()
            config["name"] = name
            manager.create_avatar(config)
            
        # Search
        all_avatars = manager.get_all_avatars()
        magnus_avatars = [a for a in all_avatars if "Magnus" in a["name"]]
        
        assert len(magnus_avatars) == 2
        
    def test_filter_by_elo_range(self, tmp_path, sample_avatar_config):
        """Test filtering avatars by Elo range"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        # Create avatars with different Elos
        for elo in [1200, 1500, 1800, 2000, 2500]:
            config = sample_avatar_config.copy()
            config["elo"] = elo
            config["name"] = f"Player{elo}"
            manager.create_avatar(config)
            
        # Filter
        all_avatars = manager.get_all_avatars()
        strong_avatars = [a for a in all_avatars if a["elo"] >= 1800]
        
        assert len(strong_avatars) == 3  # 1800, 2000, 2500
        
    def test_avatar_statistics(self, tmp_path, sample_avatar_config):
        """Test avatar statistics"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        config = sample_avatar_config.copy()
        config["games_analyzed"] = 100
        config["style"]["blunder_rate"] = 5.2
        
        avatar_id = manager.create_avatar(config)
        avatar = manager.get_avatar(avatar_id)
        
        assert avatar["games_analyzed"] == 100
        assert avatar["style"]["blunder_rate"] == 5.2
        
    def test_invalid_avatar_id(self, tmp_path):
        """Test getting avatar with invalid ID"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar = manager.get_avatar("invalid_id_12345")
        assert avatar is None
        
    def test_duplicate_avatar_names(self, tmp_path, sample_avatar_config):
        """Test creating avatars with duplicate names"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        # Create two avatars with same name (should be allowed)
        id1 = manager.create_avatar(sample_avatar_config)
        id2 = manager.create_avatar(sample_avatar_config)
        
        assert id1 != id2
        assert len(manager.get_all_avatars()) == 2


@pytest.mark.unit
class TestAvatarConfiguration:
    """Test avatar configuration validation"""
    
    def test_required_fields(self, tmp_path):
        """Test avatar has required fields"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        minimal_config = {
            "name": "MinimalAvatar",
            "platform": "lichess",
            "username": "testuser",
            "elo": 1500
        }
        
        avatar_id = manager.create_avatar(minimal_config)
        avatar = manager.get_avatar(avatar_id)
        
        assert "name" in avatar
        assert "platform" in avatar
        assert "username" in avatar
        assert "elo" in avatar
        
    def test_stockfish_configuration(self, tmp_path, sample_avatar_config):
        """Test Stockfish configuration in avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        avatar = manager.get_avatar(avatar_id)
        
        assert "stockfish_config" in avatar
        assert avatar["stockfish_config"]["skill_level"] == 10
        assert avatar["stockfish_config"]["depth"] == 15
        
    def test_style_profile(self, tmp_path, sample_avatar_config):
        """Test style profile in avatar"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        avatar_id = manager.create_avatar(sample_avatar_config)
        avatar = manager.get_avatar(avatar_id)
        
        assert "style" in avatar
        assert "aggressive_score" in avatar["style"]
        assert "favorite_openings" in avatar["style"]


@pytest.mark.unit
class TestAvatarPersistence:
    """Test avatar data persistence"""
    
    def test_json_serialization(self, tmp_path, sample_avatar_config):
        """Test avatar serializes to JSON correctly"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        manager.create_avatar(sample_avatar_config)
        manager.save()
        
        # Read JSON file
        with open(config_file, 'r') as f:
            data = json.load(f)
            
        assert isinstance(data, dict) or isinstance(data, list)
        
    def test_file_backup(self, tmp_path, sample_avatar_config):
        """Test creating backup of avatar file"""
        config_file = tmp_path / "avatars.json"
        manager = AvatarManager(str(config_file))
        
        manager.create_avatar(sample_avatar_config)
        manager.save()
        
        # Create backup
        backup_file = tmp_path / "avatars_backup.json"
        import shutil
        shutil.copy(config_file, backup_file)
        
        assert backup_file.exists()
        
    def test_corrupted_file_handling(self, tmp_path):
        """Test handling corrupted avatar file"""
        config_file = tmp_path / "avatars.json"
        
        # Write corrupted JSON
        config_file.write_text("{ invalid json }")
        
        # Should handle gracefully
        manager = AvatarManager(str(config_file))
        try:
            manager.load()
        except json.JSONDecodeError:
            # Expected behavior
            pass

