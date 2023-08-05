from enderturing import Config
from enderturing.http_client import HttpClient


class Tags:
    """Contains methods for tags.

    Args:
        config (Config): configuration to use.
        client (HttpClient): HTTP client instance to use for requests
    """

    def __init__(self, config: Config, client: HttpClient):
        self._config = config
        self._http_client = client

    def get_tags(self):
        """Gets a list of existing tags"""
        return self._http_client.get("/tags")

    def create_tag(self, obj_in):
        """Creates a new tag"""
        return self._http_client.post("/tags", json=obj_in)

    def update_tag(self, tag_id, obj_in):
        """Updates existing tag"""
        return self._http_client.put(f"/tags/{tag_id}", json=obj_in)

    def do_tagging(self, language, body, hit_threshold_category=0.7, hit_threshold_keyword=0.95):
        """Tagging"""
        return self._http_client.put(
            f"/tags/do-tagging?language={language}"
            f"&hit_threshold_category={hit_threshold_category}"
            f"&hit_threshold_keyword={hit_threshold_keyword}",
            json=body,
        )

    def delete_tag(self, tag_id):
        """Deletes a tag"""
        return self._http_client.delete(f"/tags/{tag_id}")
