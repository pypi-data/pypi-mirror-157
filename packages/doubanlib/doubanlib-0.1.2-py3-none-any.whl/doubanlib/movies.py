from re import findall as preg
from requests import get as get_url


class DouBan():
    """Some settings

    For example, you can set the proxy and the headers

    Usage:
        from doubanlib.movies import DouBan
        headers = {'User-Agent': 'Hello'}
        DouBan.set_headers(headers=headers)
    """
    __proxy = {}
    __headers = {}

    @classmethod
    def set_proxy(cls, proxy: dict):
        cls.__proxy = proxy

    @classmethod
    def get_proxy(cls) -> str:
        return cls.__proxy

    @classmethod
    def set_headers(cls, headers: dict):
        cls.__headers = headers

    @classmethod
    def get_headers(cls) -> dict:
        return cls.__headers


class MovieInfo(DouBan):
    """Create a movie object from a Douban number.

    For example, a movie is called "Love Letter", and its Douban 
    movie number is 1292220(https://movie.douban.com/subject/1292220/).

    Usage:
        from doubanlib.movies import MovieInfo
        obj = MovieInfo(1292220)
        print(obj.name)

    Attributes:
        m_id: The movie number in Douban.
    """

    def __init__(self, m_id: int):
        """Inits movie with the movie number."""

        if m_id <= 0 or not isinstance(m_id, int):
            raise ValueError('m_id must be a positive integer')

        self.m_id = m_id
        self.__index_url = 'https://movie.douban.com/subject/' + str(m_id)
        self.m_data = get_url(self.__index_url,
                              headers=self.get_headers(),
                              proxies=self.get_proxy()).text

    def __bool__(self) -> bool:
        temp = self.name
        return True if self.name else False

    def __str__(self) -> str:
        return self.m_data

    @property
    def name(self) -> str:
        temp = preg('"name": "([\s\S]*?)"', self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0]

    @property
    def chineseName(self) -> str:
        temp = preg('<title>([\s\S]*?)<\/title>', self.m_data)[0]
        if len(temp) <= 0:
            return None
        replace_ls = ['\n', '\r', '(豆瓣)']
        for i in replace_ls:
            temp = temp.replace(i, '')
        return temp.strip()

    @property
    def description(self) -> str:
        if '<span class="all hidden">' in self.m_data:
            pattern = '<span class="all hidden">([\s\S]*?)<\/span>'
        else:
            pattern = '<span property="v:summary" class="">([\s\S]*?)<\/span>'
        temp = preg(pattern, self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0].replace(' ', '').replace('\n', '')

    @property
    def pubDate(self) -> list:
        return preg(
            '<span property="v:initialReleaseDate" content="([\s\S]*?)">',
            self.m_data)

    @property
    def languages(self) -> list:
        temp = preg('语言:<\/span>([\s\S]*?)<br\/>', self.m_data)
        return [i.strip() for i in temp[0].split(' / ')]

    @property
    def alias(self) -> list:
        temp = preg('又名:<\/span>([\s\S]*?)<br\/>', self.m_data)
        if len(temp) <= 0:
            return []
        return [i.strip() for i in temp[0].split(' / ')]

    @property
    def genre(self) -> list:
        return preg('<span property="v:genre">([\s\S]*?)<\/span>', self.m_data)

    @property
    def rating(self) -> float:
        temp = preg('property="v:average">([\s\S]*?)<\/strong>', self.m_data)
        if len(temp) <= 0:
            return None
        return float(temp[0])

    @property
    def rating_per(self) -> list:
        temp = preg('<span class="rating_per">([\s\S]*?)<\/span>', self.m_data)
        return temp

    @property
    def votes(self) -> int:
        temp = preg('<span property="v:votes">([\s\S]*?)<\/span>', self.m_data)
        if len(temp) <= 0:
            return None
        return int(temp[0])

    @property
    def image(self) -> str:
        temp = preg('"image": "([\s\S]*?)",', self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0]

    @property
    def year(self) -> int:
        if '<span class="year">' in self.m_data:
            pattern = '<span class="year">\(([\s\S]*?)\)<\/span>'
        else:
            pattern = '<span property="v:initialReleaseDate" content="([\s\S]*?)-'
        temp = preg(pattern, self.m_data)
        if len(temp) <= 0:
            return None
        return int(temp[0])

    @property
    def imdb(self) -> str:
        temp = preg('IMDb:<\/span>([\s\S]*?)<br>', self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0].strip()

    @property
    def actors(self) -> list:
        temp = preg('<span class="actor">([\s\S]*?)</div>', self.m_data)
        if len(temp) <= 0:
            return []
        return preg(
            '<a href="/celebrity/([\s\S]*?)/" rel="v:starring">([\s\S]*?)</a>',
            temp[0])

    @property
    def writers(self) -> list:
        temp = preg('<span ><span class=\'pl\'>导演</span>: ([\s\S]*?)<br/>',
                    self.m_data)
        if len(temp) <= 0:
            return []
        return preg('">([\s\S]*?)<\/a>', temp[0])

    @property
    def directors(self) -> list:
        temp = preg("<span ><span class='pl'>导演</span>:([\s\S]*?)<br/>",
                    self.m_data)
        if len(temp) <= 0:
            return []
        return preg('">([\s\S]*?)<\/a>', temp[0])

    @property
    def regions(self) -> list:
        temp = preg('<span class="pl">制片国家/地区:</span>([\s\S]*?)<br/>',
                    self.m_data)
        if len(temp) <= 0:
            return []
        return [i.strip() for i in temp[0].split('/')]

    @property
    def length_tv(self) -> int:
        temp = preg('单集片长:<\/span>([\s\S]*?)<br\/>', self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0].strip()

    @property
    def length_movie(self) -> int:
        temp = preg(
            '<span property="v:runtime" content="([\s\S]*?)">([\s\S]*?)<\/span>',
            self.m_data)
        if len(temp) <= 0:
            return None
        return temp[0][1]


class MoviesTag(DouBan):
    """Create an object to get some movies.

    """

    def __init__(self,
                 tags='',
                 page=0,
                 sort='',
                 genres='',
                 country='',
                 year_range=''):
        self.tags = tags
        self.page = page
        self.sort = sort
        self.genres = genres
        self.country = country
        self.year_range = year_range
        self.__index_url = 'https://movie.douban.com/j/new_search_subjects?sort={}&range=0,10&tags={}&start={}&genres={}&countries={}&year_range={}'.format(
            self.sort, self.tags, self.page * 20, self.genres, self.country,
            self.year_range)
        self.tag_data = get_url(self.__index_url,
                                headers=self.get_headers(),
                                proxies=self.get_proxy()).json()

    def __bool__(self) -> bool:
        return False if len(self.tag_data['data']) <= 0 else True

    def get_id(self) -> list:
        id_ls = []
        for item in self.tag_data['data']:
            id_ls.append(int(item['id']))
        return id_ls
