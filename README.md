# Video Record Flask App

# Deploy
Use fpm(based on Ruby) tool to pack the app to deb file.
```bash
$ cd /home/share/video_record/
$ tree deploy/
deploy/
└── home
    └── share
        └── video_record
            ├── libUDP2HLS.so.1.0.0
            ├── record
            ├── replay.conf
            └── tsserver

3 directories, 4 files
$ fpm -s dir -t deb --deb-init record -n video_record -C deploy .
```

# Installation
```bash
$ dpkg -i video-record_1.0_amd64.deb
```
