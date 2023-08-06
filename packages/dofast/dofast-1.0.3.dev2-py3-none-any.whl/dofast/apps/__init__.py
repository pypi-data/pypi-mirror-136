import codefast as cf
from authc import gunload
from typing import List
from dofast.data.dynamic import TOKEN


class TweetText(object):
    def __init__(self, content: str) -> None:
        self.content = content

    @property
    def len(self) -> int:
        return sum([2 if cf.nstr(c).is_cn() else 1 for c in self.content])

    def __str__(self) -> str:
        return self.content


class Tweet(object):
    BOUND: int = 280

    def __init__(self, text: str, media: List[str]) -> None:
        self.text = TweetText(text)
        self.media = media

    @cf.utils.retry()
    def post(self) -> None:
        SERVER_HOST = gunload('twitter_server_host')
        if self.text.len > self.BOUND:
            raise Exception('Tweet text is too long, {}'.format(self.text.len))
        files = [('images', (cf.io.basename(m), open(m, 'rb'), 'image/png'))
                 for m in self.media]
        resp = cf.net.post(SERVER_HOST,
                           params={
                               'text': str(self.text),
                               'token': TOKEN
                           },
                           files=files)
        cf.info('Tweet response: {}'.format(resp))
        cf.info(resp.json())
