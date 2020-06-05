# DictationHelper
## Description

 **Automatic caption generation.**

No feedback when practicing listening skills? Too many "squanchy" words blocking oral comprehension? Let **DictationHelper** salvage you!

This python script aims to produce caption of a input audio or video file that helps you to understand the basic meaning of the material using API provided by **[iFlyTek]( https://www.xfyun.cn/  )**.

## Supported language

Chinese, Chinese dialects, English, French, Russian, German, Japanese, Italian, Spanish, Thai, Arabia, Korean, ... (configurable in **iFlyTek console**)

## Requirements

### Python module

In addition to the `base` environment of Anaconda 3, the following modules are required:

|    name     | version |
| :---------: | :-----: |
| `websocket` |  0.2.1  |
|             |         |

### FFmpeg

Also, installation of `FFmpeg` is necessary. Click [ http://ffmpeg.org/ ]( http://ffmpeg.org/ ) to download suitable version on your platform. Make sure that `ffmpeg` and `ffprobe` is callable by your shell (If you are a Windows user, add the bin folder of `ffmpeg` to your system path). Example :

```shell
PS E:\Files\Python\Project\DictationHelper> ffmpeg

ffmpeg version git-2020-06-03-b6d7c4c Copyright (c) 2000-2020 the FFmpeg developers
  built with gcc 9.3.1 (GCC) 20200523
  ...
  ...
  ...
Hyper fast Audio and Video encoder
usage: ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...

Use -h to get full help or, even better, run 'man ffmpeg'
```

### IFlyTek API

Sign in [Iflytek](  https://www.xfyun.cn/  ) , go to console (upper right) and create a new APP instance of "语音听写（流式版）". Here you can set your language configuration for later dictation.

![](sources/iFlyTek_console.png)

