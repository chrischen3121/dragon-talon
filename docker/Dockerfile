FROM python:3.7.8
RUN git clone --depth=1 --branch=master https://github.com/chrischen3121/dragon-talon.git /app/dragon-talon
WORKDIR /app/dragon-talon
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com .
CMD ["scrapy", "crawl", "lianjia"]
