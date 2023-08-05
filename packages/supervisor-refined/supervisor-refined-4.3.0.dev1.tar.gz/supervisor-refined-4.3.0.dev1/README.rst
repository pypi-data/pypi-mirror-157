Supervisor-Refined
==================
基于Supervisor，解决其两个问题：

   1. 显示日志时可能会遇到报错的情况
   2. 使用nginx做反向代理并设置前缀时，在Web界面进行管理会遇到404错


nginx配置
---------

::
    
    location /supervisor/ {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # hack the host https://github.com/Supervisor/supervisor/issues/251
        proxy_set_header Host $http_host/supervisor/index.html;
        proxy_redirect off;
        proxy_buffering off;
        proxy_max_temp_file_size 0;
        rewrite ^/supervisor/(.*)$ /$1 break;
        proxy_pass http://supervisor-host:9001/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }



Supervisor is a client/server system that allows its users to
control a number of processes on UNIX-like operating systems.

Supported Platforms
-------------------

Supervisor has been tested and is known to run on Linux (Ubuntu), Mac OS X
(10.4, 10.5, 10.6), and Solaris (10 for Intel) and FreeBSD 6.1.  It will
likely work fine on most UNIX systems.

Supervisor will not run at all under any version of Windows.

Supervisor is intended to work on Python 3 version 3.4 or later
and on Python 2 version 2.7.

Documentation
-------------

You can view the current Supervisor documentation online `in HTML format
<http://supervisord.org/>`_ .  This is where you should go for detailed
installation and configuration documentation.

Reporting Bugs and Viewing the Source Repository
------------------------------------------------

Please report bugs in the `GitHub issue tracker
<https://github.com/Supervisor/supervisor/issues>`_.

You can view the source repository for supervisor via
`https://github.com/Supervisor/supervisor
<https://github.com/Supervisor/supervisor>`_.

Contributing
------------

We'll review contributions from the community in
`pull requests <https://help.github.com/articles/using-pull-requests>`_
on GitHub.
