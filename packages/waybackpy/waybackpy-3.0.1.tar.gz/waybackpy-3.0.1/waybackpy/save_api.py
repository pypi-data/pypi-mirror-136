import re
import time
import requests

from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .utils import DEFAULT_USER_AGENT
from .exceptions import MaximumSaveRetriesExceeded


class WaybackMachineSaveAPI:

    """
    WaybackMachineSaveAPI class provides an interface for saving URLs on the
    Wayback Machine.
    """

    def __init__(self, url, user_agent=DEFAULT_USER_AGENT, max_tries=8):
        self.url = str(url).strip().replace(" ", "%20")
        self.request_url = "https://web.archive.org/save/" + self.url
        self.user_agent = user_agent
        self.request_headers = {"User-Agent": self.user_agent}
        self.max_tries = max_tries
        self.total_save_retries = 5
        self.backoff_factor = 0.5
        self.status_forcelist = [500, 502, 503, 504]
        self._archive_url = None
        self.instance_birth_time = datetime.utcnow()

    @property
    def archive_url(self):
        """
        Returns the archive URL is already cached by _archive_url
        else invoke the save method to save the archive which returns the
        archive thus we return the methods return value.
        """

        if self._archive_url:
            return self._archive_url
        else:
            return self.save()

    def get_save_request_headers(self):
        """
        Creates a session and tries 'retries' number of times to
        retrieve the archive.

        If successful in getting the response, sets the headers, status_code
        and response_url attributes.

        The archive is usually in the headers but it can also be the response URL
        as the Wayback Machine redirects to the archive after a successful capture
        of the webpage.

        Wayback Machine's save API is known
        to be very unreliable thus if it fails first check opening
        the response URL yourself in the browser.
        """
        session = requests.Session()
        retries = Retry(
            total=self.total_save_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        self.response = session.get(self.request_url, headers=self.request_headers)
        self.headers = (
            self.response.headers
        )  # <class 'requests.structures.CaseInsensitiveDict'>
        self.status_code = self.response.status_code
        self.response_url = self.response.url
        session.close()

    def archive_url_parser(self):
        """
        Three regexen (like oxen?) are used to search for the
        archive URL in the headers and finally look in the response URL
        for the archive URL.
        """

        regex1 = r"Content-Location: (/web/[0-9]{14}/.*)"
        match = re.search(regex1, str(self.headers))
        if match:
            return "https://web.archive.org" + match.group(1)

        regex2 = r"rel=\"memento.*?(web\.archive\.org/web/[0-9]{14}/.*?)>"
        match = re.search(regex2, str(self.headers))
        if match:
            return "https://" + match.group(1)

        regex3 = r"X-Cache-Key:\shttps(.*)[A-Z]{2}"
        match = re.search(regex3, str(self.headers))
        if match:
            return "https" + match.group(1)

        if self.response_url:
            self.response_url = self.response_url.strip()
            if "web.archive.org/web" in self.response_url:
                regex = r"web\.archive\.org/web/(?:[0-9]*?)/(?:.*)$"
                match = re.search(regex, self.response_url)
                if match:
                    return "https://" + match.group(0)

    def sleep(self, tries):
        """
        Ensure that the we wait some time before succesive retries so that we
        don't waste the retries before the page is even captured by the Wayback
        Machine crawlers also ensures that we are not putting too much load on
        the Wayback Machine's save API.

        If tries are multiple of 3 sleep 10 seconds else sleep 5 seconds.
        """

        sleep_seconds = 5
        if tries % 3 == 0:
            sleep_seconds = 10
        time.sleep(sleep_seconds)

    def timestamp(self):
        """
        Read the timestamp off the archive URL and convert the Wayback Machine
        timestamp to datetime object.

        Also check if the time on archive is URL and compare it to instance birth
        time.

        If time on the archive is older than the instance creation time set the cached_save
        to True else set it to False. The flag can be used to check if the Wayback Machine
        didn't serve a Cached URL. It is quite common for the Wayback Machine to serve
        cached archive if last archive was captured before last 45 minutes.
        """
        m = re.search(
            r"https?://web\.archive.org/web/([0-9]{14})/http", self._archive_url
        )
        string_timestamp = m.group(1)
        timestamp = datetime.strptime(string_timestamp, "%Y%m%d%H%M%S")

        timestamp_unixtime = time.mktime(timestamp.timetuple())
        instance_birth_time_unixtime = time.mktime(self.instance_birth_time.timetuple())

        if timestamp_unixtime < instance_birth_time_unixtime:
            self.cached_save = True
        else:
            self.cached_save = False

        return timestamp

    def save(self):
        """
        Calls the SavePageNow API of the Wayback Machine with required parameters
        and headers to save the URL.

        Raises MaximumSaveRetriesExceeded is maximum retries are exhausted but still
        we were unable to retrieve the archive from the Wayback Machine.
        """

        self.saved_archive = None
        tries = 0

        while True:

            tries += 1

            if tries >= self.max_tries:
                raise MaximumSaveRetriesExceeded(
                    "Tried %s times but failed to save and retrieve the" % str(tries)
                    + " archive for %s.\nResponse URL:\n%s \nResponse Header:\n%s\n"
                    % (self.url, self.response_url, str(self.headers)),
                )

            if not self.saved_archive:

                if tries > 1:
                    self.sleep(tries)

                self.get_save_request_headers()
                self.saved_archive = self.archive_url_parser()

                if not self.saved_archive:
                    continue
                else:
                    self._archive_url = self.saved_archive
                    self.timestamp()
                    return self.saved_archive
