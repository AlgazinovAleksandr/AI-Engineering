Useful bash commands (except for the simplest ones everybody is aware of) for daily use:

touch - create a file. Ex: touch useful_command.md

cat - list the content of a file. Ex: cat useful_command.md

grep - search for a pattern in a file. Ex: grep "useful" useful_command.md

vi - edit a file. Ex: vi useful_command.md. Once you enter the vim editor, you can press i to enter insert mode, and then you can edit the file. To save the changes and exit, press Esc, then type :wq, and press Enter

**I have over 2 years of experience working with vim. I mean two years ago I opened it, and since then I can't exit it**. I wrote it using vim

head - list the first few lines of a file. Ex: head -n 5 useful_command.md

tail - list the last few lines of a file. VERY useful for logs. Ex: tail -n 5 useful_command.md

curl - send an HTTP request to a server. Examples:

curl https://algazinovaleksandr.github.io/research_and_projects/ - get the content of a webpage (and check out what I'm working on right now)

ssh - connect to a remote server. Ex: ssh user@server

ps - list the processes running on a server. Ex: ps aux

htop - check the processes running on a server

nvidia-smi - check the status of the GPU

kill -9 - kill a process. Ex: kill -9 1234
