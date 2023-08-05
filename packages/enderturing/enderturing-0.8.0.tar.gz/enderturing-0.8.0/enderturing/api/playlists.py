from enderturing import Config
from enderturing.http_client import HttpClient


class Playlists:
    def __init__(self, config: Config, client: HttpClient):
        """
        Args:
            config (Config): configuration to use.
            client (HttpClient): HTTP client instance to use for requests
        """
        self._config = config
        self._http_client = client

    def get_tree(self):
        """Gets a playlists tree"""
        return self._http_client.get("/playlists/tree")

    def save_tree(self, obj_in):
        """Saves a playlists tree"""
        return self._http_client.post("/playlists/tree", json=obj_in)

    def get_items(self, session_id):
        """Gets a sessions playlist items"""
        return self._http_client.get(f"/playlists/items?session_id={session_id}")

    def create_playlist_item(self, playlist_id, obj_in):
        """Creates a playlist item"""
        return self._http_client.post(f"/playlists/{playlist_id}/items", json=obj_in)

    def get_playlist_items(self, playlist_id):
        """Gets a playlist items"""
        return self._http_client.get(f"/playlists/{playlist_id}/items")

    def update_playlist_item(self, playlist_id, item_id, obj_in):
        """Updates a playlist item"""
        return self._http_client.put(f"/playlists/{playlist_id}/items/{item_id}", json=obj_in)

    def delete_playlist_item(self, playlist_id, item_id):
        """Deletes a playlist item"""
        return self._http_client.delete(f"/playlists/{playlist_id}/items/{item_id}")
