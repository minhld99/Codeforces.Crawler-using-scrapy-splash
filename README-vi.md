1. Cài đặt môi trường ảo (conda hoặc virtualenv đều được)
```
($ conda create --name crawler python) 
$ virtualenv env
$ source env/bin/activate
```
2. Cài đặt docker thông qua homebrew (để chạy thư viện scrapy-splash)
```
$ brew tap phinze/homebrew-cask
$ brew install brew-cask
$ brew cask install docker
($ open /Applications/Docker.app) --> test xem cài oke chưa
(Uninstall: $ brew cask uninstall docker)
$ sudo docker pull scrapinghub/splash
$ sudo docker run -p 8050:8050 scrapinghub/splash --> Những lần sau chỉ cần mở docker chạy lệnh này
(Link on browser: localhost:8050) --> test server
```
3. Cài đặt các requirements (nên cài trên môi trường ảo):
```
pip3 install -r requirements.txt
```
4. Run:
```
scrapy crawl cf_submission
```
### Learn lua to write splash in 15 minutes: http://tylerneylon.com/a/learn-lua/
