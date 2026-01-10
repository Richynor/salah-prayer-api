{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red226\green158\blue107;\red21\green21\blue21;\red247\green249\blue250;
\red220\green229\blue239;\red129\green201\blue99;\red91\green169\blue224;\red239\green151\blue241;\red224\green203\blue103;
\red184\green130\blue220;\red123\green143\blue171;}
{\*\expandedcolortbl;;\cssrgb\c91373\c68235\c49412;\cssrgb\c10588\c10588\c10980;\cssrgb\c97647\c98039\c98431;
\cssrgb\c89020\c91765\c94902;\cssrgb\c56863\c81569\c46275;\cssrgb\c42353\c72157\c90196;\cssrgb\c95686\c67843\c95686;\cssrgb\c90196\c82745\c47843;
\cssrgb\c77647\c60000\c89020;\cssrgb\c55294\c63137\c72549;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs26 \cf2 \cb3 \expnd0\expndtw0\kerning0
from\cf4  fastapi \cf2 import\cf4  FastAPI\
\cf2 from\cf4  fastapi\cf5 .\cf4 middleware\cf5 .\cf4 cors \cf2 import\cf4  CORSMiddleware\
\cf2 from\cf4  pydantic \cf2 import\cf4  BaseModel\
\cf2 from\cf4  datetime \cf2 import\cf4  datetime\
\cf2 from\cf4  typing \cf2 import\cf4  Optional\
\cf2 import\cf4  math\
\
app \cf2 =\cf4  FastAPI\cf5 (\cf4 title\cf2 =\cf6 "Fazilet Prayer Times API"\cf5 )\cf4 \
\
app\cf5 .\cf4 add_middleware\cf5 (\cf4 \
    CORSMiddleware\cf5 ,\cf4 \
    allow_origins\cf2 =\cf5 [\cf6 "*"\cf5 ],\cf4 \
    allow_methods\cf2 =\cf5 [\cf6 "*"\cf5 ],\cf4 \
    allow_headers\cf2 =\cf5 [\cf6 "*"\cf5 ],\cf4 \
\cf5 )\cf4 \
\
\cf2 class\cf4  \cf7 PrayerRequest\cf5 (\cf4 BaseModel\cf5 ):\cf4 \
    latitude\cf5 :\cf4  \cf8 float\cf4 \
    longitude\cf5 :\cf4  \cf8 float\cf4 \
    timezone_offset\cf5 :\cf4  \cf8 float\cf4 \
    country\cf5 :\cf4  \cf8 str\cf4 \
    date\cf5 :\cf4  Optional\cf5 [\cf8 str\cf5 ]\cf4  \cf2 =\cf4  \cf9 None\cf4 \
\
\cf5 @app.get(\cf6 "/"\cf5 )\cf4 \
\cf2 async\cf4  \cf2 def\cf4  \cf10 root\cf5 ():\cf4 \
    \cf2 return\cf4  \cf5 \{\cf4 \
        \cf6 "message"\cf5 :\cf4  \cf6 "Fazilet Prayer Times API"\cf5 ,\cf4 \
        \cf6 "status"\cf5 :\cf4  \cf6 "active"\cf5 ,\cf4 \
        \cf6 "endpoint"\cf5 :\cf4  \cf6 "POST /prayer-times/custom"\cf4 \
    \cf5 \}\cf4 \
\
\cf5 @app.get(\cf6 "/health"\cf5 )\cf4 \
\cf2 async\cf4  \cf2 def\cf4  \cf10 health\cf5 ():\cf4 \
    \cf2 return\cf4  \cf5 \{\cf6 "status"\cf5 :\cf4  \cf6 "healthy"\cf5 \}\cf4 \
\
\cf5 @app.post(\cf6 "/prayer-times/custom"\cf5 )\cf4 \
\cf2 async\cf4  \cf2 def\cf4  \cf10 get_prayer_times\cf5 (\cf4 request\cf5 :\cf4  PrayerRequest\cf5 ):\cf4 \
    \cf2 if\cf4  request\cf5 .\cf4 date\cf5 :\cf4 \
        \cf2 try\cf5 :\cf4 \
            target_date \cf2 =\cf4  datetime\cf5 .\cf4 strptime\cf5 (\cf4 request\cf5 .\cf4 date\cf5 ,\cf4  \cf6 "%Y-%m-%d"\cf5 )\cf4 \
        \cf2 except\cf5 :\cf4 \
            target_date \cf2 =\cf4  datetime\cf5 .\cf4 now\cf5 ()\cf4 \
    \cf2 else\cf5 :\cf4 \
        target_date \cf2 =\cf4  datetime\cf5 .\cf4 now\cf5 ()\cf4 \
    \
    \cf11 # Calculate Qibla\cf4 \
    kaaba_lat \cf2 =\cf4  \cf9 21.4225\cf4 \
    kaaba_lon \cf2 =\cf4  \cf9 39.8262\cf4 \
    \
    lat1 \cf2 =\cf4  math\cf5 .\cf4 radians\cf5 (\cf4 request\cf5 .\cf4 latitude\cf5 )\cf4 \
    lon1 \cf2 =\cf4  math\cf5 .\cf4 radians\cf5 (\cf4 request\cf5 .\cf4 longitude\cf5 )\cf4 \
    lat2 \cf2 =\cf4  math\cf5 .\cf4 radians\cf5 (\cf4 kaaba_lat\cf5 )\cf4 \
    lon2 \cf2 =\cf4  math\cf5 .\cf4 radians\cf5 (\cf4 kaaba_lon\cf5 )\cf4 \
    \
    dlon \cf2 =\cf4  lon2 \cf2 -\cf4  lon1\
    \
    y \cf2 =\cf4  math\cf5 .\cf4 sin\cf5 (\cf4 dlon\cf5 )\cf4  \cf2 *\cf4  math\cf5 .\cf4 cos\cf5 (\cf4 lat2\cf5 )\cf4 \
    x \cf2 =\cf4  math\cf5 .\cf4 cos\cf5 (\cf4 lat1\cf5 )\cf4  \cf2 *\cf4  math\cf5 .\cf4 sin\cf5 (\cf4 lat2\cf5 )\cf4  \cf2 -\cf4  math\cf5 .\cf4 sin\cf5 (\cf4 lat1\cf5 )\cf4  \cf2 *\cf4  math\cf5 .\cf4 cos\cf5 (\cf4 lat2\cf5 )\cf4  \cf2 *\cf4  math\cf5 .\cf4 cos\cf5 (\cf4 dlon\cf5 )\cf4 \
    \
    bearing \cf2 =\cf4  math\cf5 .\cf4 atan2\cf5 (\cf4 y\cf5 ,\cf4  x\cf5 )\cf4 \
    qibla \cf2 =\cf4  math\cf5 .\cf4 degrees\cf5 (\cf4 bearing\cf5 )\cf4 \
    qibla \cf2 =\cf4  \cf5 (\cf4 qibla \cf2 +\cf4  \cf9 360\cf5 )\cf4  \cf2 %\cf4  \cf9 360\cf4 \
    \
    \cf2 return\cf4  \cf5 \{\cf4 \
        \cf6 "location"\cf5 :\cf4  \cf6 f"Custom (\cf5 \{\cf4 request\cf5 .\cf4 latitude\cf5 :\cf4 .4f\cf5 \}\cf6 , \cf5 \{\cf4 request\cf5 .\cf4 longitude\cf5 :\cf4 .4f\cf5 \}\cf6 )"\cf5 ,\cf4 \
        \cf6 "date"\cf5 :\cf4  target_date\cf5 .\cf4 strftime\cf5 (\cf6 "%Y-%m-%d"\cf5 ),\cf4 \
        \cf6 "country"\cf5 :\cf4  request\cf5 .\cf4 country\cf5 ,\cf4 \
        \cf6 "latitude"\cf5 :\cf4  request\cf5 .\cf4 latitude\cf5 ,\cf4 \
        \cf6 "longitude"\cf5 :\cf4  request\cf5 .\cf4 longitude\cf5 ,\cf4 \
        \cf6 "timezone_offset"\cf5 :\cf4  request\cf5 .\cf4 timezone_offset\cf5 ,\cf4 \
        \cf6 "prayer_times"\cf5 :\cf4  \cf5 \{\cf4 \
            \cf6 "fajr"\cf5 :\cf4  \cf6 "06:00"\cf5 ,\cf4 \
            \cf6 "sunrise"\cf5 :\cf4  \cf6 "08:00"\cf5 ,\cf4 \
            \cf6 "dhuhr"\cf5 :\cf4  \cf6 "12:00"\cf5 ,\cf4 \
            \cf6 "asr"\cf5 :\cf4  \cf6 "15:00"\cf5 ,\cf4 \
            \cf6 "maghrib"\cf5 :\cf4  \cf6 "18:00"\cf5 ,\cf4 \
            \cf6 "isha"\cf5 :\cf4  \cf6 "20:00"\cf4 \
        \cf5 \},\cf4 \
        \cf6 "qibla_direction"\cf5 :\cf4  \cf8 round\cf5 (\cf4 qibla\cf5 ,\cf4  \cf9 2\cf5 )\cf4 \
    \cf5 \}\cf4 \
\
\cf2 if\cf4  __name__ \cf2 ==\cf4  \cf6 "__main__"\cf5 :\cf4 \
    \cf2 import\cf4  uvicorn\
    uvicorn\cf5 .\cf4 run\cf5 (\cf4 app\cf5 ,\cf4  host\cf2 =\cf6 "0.0.0.0"\cf5 ,\cf4  port\cf2 =\cf9 8000\cf5 )}