# 변경 이력

## 2026-05-06 — 이메일 발송 Resend → Gmail SMTP 전환

**배경:** Resend의 `onboarding@resend.dev` 샌더는 계정 소유자 이메일 1개에만 발송 가능. 다수 수신자(RECIPIENT_EMAILS)에게 보내려면 커스텀 도메인 인증이 필요하나, 별도 도메인 없음.

**변경 내용:**
- `core/mailer.py`: Resend HTTP API → Gmail SMTP(`smtplib.SMTP_SSL`) 교체. 수신자별 개별 발송으로 주소 노출 없음.
- `config/settings.py`: `RESEND_API_KEY`, `EMAIL_FROM` 제거 → `GMAIL_USER`, `GMAIL_APP_PASSWORD` 추가
- `.github/workflows/news.yml`: `RESEND_API_KEY` → `GMAIL_USER`, `GMAIL_APP_PASSWORD` 시크릿으로 교체
- `.env.example`: Gmail SMTP 항목으로 업데이트
- `README.md`, `GUIDE.md`: 문서 전반 Resend → Gmail SMTP 반영

**GitHub Secrets 현황 (2026-05-06 기준):**
| 시크릿 | 상태 |
|--------|------|
| `GMAIL_USER` | ✅ 등록 |
| `GMAIL_APP_PASSWORD` | ✅ 등록 |
| `RECIPIENT_EMAILS` | ✅ 등록 (3명) |
| `RESEND_API_KEY` | 미사용 (삭제 가능) |
| `RECIPIENT_EMAIL` | 미사용 (삭제 가능) |

---

## 2026-04-29 — GitHub Actions 실행 로그

2026-04-29T11:39:08.3910687Z Current runner version: '2.334.0'
2026-04-29T11:39:08.3933794Z ##[group]Runner Image Provisioner
2026-04-29T11:39:08.3934724Z Hosted Compute Agent
2026-04-29T11:39:08.3935325Z Version: 20260213.493
2026-04-29T11:39:08.3935906Z Commit: 5c115507f6dd24b8de37d8bbe0bb4509d0cc0fa3
2026-04-29T11:39:08.3936681Z Build Date: 2026-02-13T00:28:41Z
2026-04-29T11:39:08.3937642Z Worker ID: {ce390395-b39d-4350-850b-bb72d18ce622}
2026-04-29T11:39:08.3938330Z Azure Region: westus
2026-04-29T11:39:08.3938963Z ##[endgroup]
2026-04-29T11:39:08.3940402Z ##[group]Operating System
2026-04-29T11:39:08.3941084Z Ubuntu
2026-04-29T11:39:08.3941643Z 24.04.4
2026-04-29T11:39:08.3942095Z LTS
2026-04-29T11:39:08.3942627Z ##[endgroup]
2026-04-29T11:39:08.3943180Z ##[group]Runner Image
2026-04-29T11:39:08.3943758Z Image: ubuntu-24.04
2026-04-29T11:39:08.3944385Z Version: 20260413.86.1
2026-04-29T11:39:08.3945605Z Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20260413.86/images/ubuntu/Ubuntu2404-Readme.md
2026-04-29T11:39:08.3947358Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20260413.86
2026-04-29T11:39:08.3948338Z ##[endgroup]
2026-04-29T11:39:08.3949656Z ##[group]GITHUB_TOKEN Permissions
2026-04-29T11:39:08.3951487Z Contents: write
2026-04-29T11:39:08.3952155Z Metadata: read
2026-04-29T11:39:08.3952727Z Pages: write
2026-04-29T11:39:08.3953224Z ##[endgroup]
2026-04-29T11:39:08.3955448Z Secret source: Actions
2026-04-29T11:39:08.3956246Z Prepare workflow directory
2026-04-29T11:39:08.4308998Z Prepare all required actions
2026-04-29T11:39:08.4365548Z Getting action download info
2026-04-29T11:39:09.0008644Z Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
2026-04-29T11:39:09.1300548Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
2026-04-29T11:39:09.2091637Z Download action repository 'actions/upload-pages-artifact@v3' (SHA:56afc609e74202658d3ffba0e8f6dda462b719fa)
2026-04-29T11:39:09.6433238Z Download action repository 'actions/deploy-pages@v4' (SHA:d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e)
2026-04-29T11:39:10.5460323Z Getting action download info
2026-04-29T11:39:10.7771962Z Download action repository 'actions/upload-artifact@v4' (SHA:ea165f8d65b6e75b540449e92b4886f43607fa02)
2026-04-29T11:39:10.9008516Z Complete job name: run
2026-04-29T11:39:10.9705350Z ##[group]Run actions/checkout@v4
2026-04-29T11:39:10.9705991Z with:
2026-04-29T11:39:10.9706257Z   repository: chamgil71/dailynews
2026-04-29T11:39:10.9706726Z   token: ***
2026-04-29T11:39:10.9707604Z   ssh-strict: true
2026-04-29T11:39:10.9707970Z   ssh-user: git
2026-04-29T11:39:10.9708374Z   persist-credentials: true
2026-04-29T11:39:10.9708662Z   clean: true
2026-04-29T11:39:10.9708922Z   sparse-checkout-cone-mode: true
2026-04-29T11:39:10.9709227Z   fetch-depth: 1
2026-04-29T11:39:10.9709479Z   fetch-tags: false
2026-04-29T11:39:10.9709745Z   show-progress: true
2026-04-29T11:39:10.9710012Z   lfs: false
2026-04-29T11:39:10.9710279Z   submodules: false
2026-04-29T11:39:10.9710549Z   set-safe-directory: true
2026-04-29T11:39:10.9711135Z ##[endgroup]
2026-04-29T11:39:11.0820814Z Syncing repository: chamgil71/dailynews
2026-04-29T11:39:11.0822219Z ##[group]Getting Git version info
2026-04-29T11:39:11.0822690Z Working directory is '/home/runner/work/dailynews/dailynews'
2026-04-29T11:39:11.0823398Z [command]/usr/bin/git version
2026-04-29T11:39:11.0868556Z git version 2.53.0
2026-04-29T11:39:11.0894137Z ##[endgroup]
2026-04-29T11:39:11.0908277Z Temporarily overriding HOME='/home/runner/work/_temp/f37074f5-ff58-4766-986e-99a041e5c716' before making global git config changes
2026-04-29T11:39:11.0909266Z Adding repository directory to the temporary git global config as a safe directory
2026-04-29T11:39:11.0913478Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/dailynews/dailynews
2026-04-29T11:39:11.0943273Z Deleting the contents of '/home/runner/work/dailynews/dailynews'
2026-04-29T11:39:11.0946817Z ##[group]Initializing the repository
2026-04-29T11:39:11.0951186Z [command]/usr/bin/git init /home/runner/work/dailynews/dailynews
2026-04-29T11:39:11.1042273Z hint: Using 'master' as the name for the initial branch. This default branch name
2026-04-29T11:39:11.1043327Z hint: will change to "main" in Git 3.0. To configure the initial branch name
2026-04-29T11:39:11.1044297Z hint: to use in all of your new repositories, which will suppress this warning,
2026-04-29T11:39:11.1044942Z hint: call:
2026-04-29T11:39:11.1045231Z hint:
2026-04-29T11:39:11.1045584Z hint: 	git config --global init.defaultBranch <name>
2026-04-29T11:39:11.1045963Z hint:
2026-04-29T11:39:11.1046326Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
2026-04-29T11:39:11.1046879Z hint: 'development'. The just-created branch can be renamed via this command:
2026-04-29T11:39:11.1047719Z hint:
2026-04-29T11:39:11.1047983Z hint: 	git branch -m <name>
2026-04-29T11:39:11.1048263Z hint:
2026-04-29T11:39:11.1048637Z hint: Disable this message with "git config set advice.defaultBranchName false"
2026-04-29T11:39:11.1049259Z Initialized empty Git repository in /home/runner/work/dailynews/dailynews/.git/
2026-04-29T11:39:11.1055577Z [command]/usr/bin/git remote add origin https://github.com/chamgil71/dailynews
2026-04-29T11:39:11.1083778Z ##[endgroup]
2026-04-29T11:39:11.1084368Z ##[group]Disabling automatic garbage collection
2026-04-29T11:39:11.1088206Z [command]/usr/bin/git config --local gc.auto 0
2026-04-29T11:39:11.1115214Z ##[endgroup]
2026-04-29T11:39:11.1115923Z ##[group]Setting up auth
2026-04-29T11:39:11.1122107Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-04-29T11:39:11.1151173Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-04-29T11:39:11.1432585Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-04-29T11:39:11.1460480Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-04-29T11:39:11.1675781Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-04-29T11:39:11.1704211Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-04-29T11:39:11.1918510Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
2026-04-29T11:39:11.1950915Z ##[endgroup]
2026-04-29T11:39:11.1951680Z ##[group]Fetching the repository
2026-04-29T11:39:11.1959451Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +60e0e7f7949f7e965cda62a9f5db0791b2665807:refs/remotes/origin/main
2026-04-29T11:39:11.9118094Z From https://github.com/chamgil71/dailynews
2026-04-29T11:39:11.9119120Z  * [new ref]         60e0e7f7949f7e965cda62a9f5db0791b2665807 -> origin/main
2026-04-29T11:39:11.9145291Z ##[endgroup]
2026-04-29T11:39:11.9145962Z ##[group]Determining the checkout info
2026-04-29T11:39:11.9148398Z ##[endgroup]
2026-04-29T11:39:11.9153246Z [command]/usr/bin/git sparse-checkout disable
2026-04-29T11:39:11.9189386Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2026-04-29T11:39:11.9213922Z ##[group]Checking out the ref
2026-04-29T11:39:11.9217893Z [command]/usr/bin/git checkout --progress --force -B main refs/remotes/origin/main
2026-04-29T11:39:11.9397535Z Switched to a new branch 'main'
2026-04-29T11:39:11.9400510Z branch 'main' set up to track 'origin/main'.
2026-04-29T11:39:11.9406615Z ##[endgroup]
2026-04-29T11:39:11.9440925Z [command]/usr/bin/git log -1 --format=%H
2026-04-29T11:39:11.9462393Z 60e0e7f7949f7e965cda62a9f5db0791b2665807
2026-04-29T11:39:11.9760961Z ##[group]Run actions/setup-python@v5
2026-04-29T11:39:11.9761474Z with:
2026-04-29T11:39:11.9761706Z   python-version: 3.11
2026-04-29T11:39:11.9761971Z   cache: pip
2026-04-29T11:39:11.9762274Z   check-la***: false
2026-04-29T11:39:11.9762643Z   token: ***
2026-04-29T11:39:11.9762893Z   update-environment: true
2026-04-29T11:39:11.9763187Z   allow-prereleases: false
2026-04-29T11:39:11.9763461Z   freethreaded: false
2026-04-29T11:39:11.9763716Z ##[endgroup]
2026-04-29T11:39:12.1420616Z ##[group]Installed versions
2026-04-29T11:39:12.1529595Z Successfully set up CPython (3.11.15)
2026-04-29T11:39:12.1530613Z ##[endgroup]
2026-04-29T11:39:12.2285794Z [command]/opt/hostedtoolcache/Python/3.11.15/x64/bin/pip cache dir
2026-04-29T11:39:13.3937314Z /home/runner/.cache/pip
2026-04-29T11:39:13.6936839Z Cache hit for: setup-python-Linux-x64-24.04-Ubuntu-python-3.11.15-pip-cc177e0a319e2b366e42ffbff4d20b32e7f9f00ab75eb7e3434e6f9155173566
2026-04-29T11:39:14.9975875Z Received 5940528 of 26912048 (22.1%), 5.7 MBs/sec
2026-04-29T11:39:15.3520563Z Received 26912048 of 26912048 (100.0%), 18.9 MBs/sec
2026-04-29T11:39:15.3521214Z Cache Size: ~26 MB (26912048 B)
2026-04-29T11:39:15.3613844Z [command]/usr/bin/tar -xf /home/runner/work/_temp/c6dde9ad-bf44-4b50-8433-74e139d0291f/cache.tzst -P -C /home/runner/work/dailynews/dailynews --use-compress-program unzstd
2026-04-29T11:39:15.4267549Z Cache restored successfully
2026-04-29T11:39:15.4285632Z Cache restored from key: setup-python-Linux-x64-24.04-Ubuntu-python-3.11.15-pip-cc177e0a319e2b366e42ffbff4d20b32e7f9f00ab75eb7e3434e6f9155173566
2026-04-29T11:39:15.4425058Z ##[group]Run pip install -r requirements.txt
2026-04-29T11:39:15.4425472Z [36;1mpip install -r requirements.txt[0m
2026-04-29T11:39:15.4452582Z shell: /usr/bin/bash -e {0}
2026-04-29T11:39:15.4452866Z env:
2026-04-29T11:39:15.4453138Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:15.4453600Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:39:15.4454063Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:15.4454471Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:15.4454851Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:15.4455231Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:39:15.4455549Z ##[endgroup]
2026-04-29T11:39:16.4429920Z Collecting anthropic==0.84.0 (from -r requirements.txt (line 1))
2026-04-29T11:39:16.4445550Z   Using cached anthropic-0.84.0-py3-none-any.whl.metadata (3.0 kB)
2026-04-29T11:39:16.4545615Z Collecting feedparser==6.0.12 (from -r requirements.txt (line 2))
2026-04-29T11:39:16.4559596Z   Using cached feedparser-6.0.12-py3-none-any.whl.metadata (2.7 kB)
2026-04-29T11:39:16.4659560Z Collecting Jinja2==3.1.6 (from -r requirements.txt (line 3))
2026-04-29T11:39:16.4673981Z   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
2026-04-29T11:39:16.4779020Z Collecting markdown2==2.5.3 (from -r requirements.txt (line 4))
2026-04-29T11:39:16.4794057Z   Using cached markdown2-2.5.3-py3-none-any.whl.metadata (2.1 kB)
2026-04-29T11:39:16.5257273Z Collecting openai==2.28.0 (from -r requirements.txt (line 5))
2026-04-29T11:39:16.5279042Z   Using cached openai-2.28.0-py3-none-any.whl.metadata (29 kB)
2026-04-29T11:39:16.5413384Z Collecting openpyxl==3.1.5 (from -r requirements.txt (line 6))
2026-04-29T11:39:16.5426701Z   Using cached openpyxl-3.1.5-py2.py3-none-any.whl.metadata (2.5 kB)
2026-04-29T11:39:16.6694676Z Collecting protobuf==7.34.0 (from -r requirements.txt (line 7))
2026-04-29T11:39:16.6709353Z   Using cached protobuf-7.34.0-cp310-abi3-manylinux2014_x86_64.whl.metadata (595 bytes)
2026-04-29T11:39:16.6810227Z Collecting python-dotenv==1.2.2 (from -r requirements.txt (line 8))
2026-04-29T11:39:16.6823481Z   Using cached python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
2026-04-29T11:39:16.6988864Z Collecting Requests==2.32.5 (from -r requirements.txt (line 9))
2026-04-29T11:39:16.7001861Z   Using cached requests-2.32.5-py3-none-any.whl.metadata (4.9 kB)
2026-04-29T11:39:16.7153779Z Collecting urllib3==2.6.3 (from -r requirements.txt (line 10))
2026-04-29T11:39:16.7174458Z   Using cached urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
2026-04-29T11:39:16.7407295Z Collecting google-genai>=0.8.0 (from -r requirements.txt (line 11))
2026-04-29T11:39:16.7429030Z   Using cached google_genai-1.73.1-py3-none-any.whl.metadata (52 kB)
2026-04-29T11:39:16.7599748Z Collecting anyio<5,>=3.5.0 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.7612650Z   Using cached anyio-4.13.0-py3-none-any.whl.metadata (4.5 kB)
2026-04-29T11:39:16.7687724Z Collecting distro<2,>=1.7.0 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.7700899Z   Using cached distro-1.9.0-py3-none-any.whl.metadata (6.8 kB)
2026-04-29T11:39:16.7776289Z Collecting docstring-parser<1,>=0.15 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.7789652Z   Using cached docstring_parser-0.18.0-py3-none-any.whl.metadata (3.5 kB)
2026-04-29T11:39:16.7918251Z Collecting httpx<1,>=0.25.0 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.7931534Z   Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
2026-04-29T11:39:16.8646373Z Collecting jiter<1,>=0.4.0 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.8660502Z   Using cached jiter-0.14.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.2 kB)
2026-04-29T11:39:16.9635908Z Collecting pydantic<3,>=1.9.0 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.9650059Z   Using cached pydantic-2.13.3-py3-none-any.whl.metadata (108 kB)
2026-04-29T11:39:16.9745902Z Collecting sniffio (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.9759096Z   Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
2026-04-29T11:39:16.9870932Z Collecting typing-extensions<5,>=4.10 (from anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:16.9883917Z   Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
2026-04-29T11:39:16.9953348Z Collecting sgmllib3k (from feedparser==6.0.12->-r requirements.txt (line 2))
2026-04-29T11:39:16.9954923Z   Using cached sgmllib3k-1.0.0-py3-none-any.whl
2026-04-29T11:39:17.0594450Z Collecting MarkupSafe>=2.0 (from Jinja2==3.1.6->-r requirements.txt (line 3))
2026-04-29T11:39:17.0609140Z   Using cached markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
2026-04-29T11:39:17.0885287Z Collecting tqdm>4 (from openai==2.28.0->-r requirements.txt (line 5))
2026-04-29T11:39:17.0898062Z   Using cached tqdm-4.67.3-py3-none-any.whl.metadata (57 kB)
2026-04-29T11:39:17.1016679Z Collecting et-xmlfile (from openpyxl==3.1.5->-r requirements.txt (line 6))
2026-04-29T11:39:17.1030049Z   Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
2026-04-29T11:39:17.1874440Z Collecting charset_normalizer<4,>=2 (from Requests==2.32.5->-r requirements.txt (line 9))
2026-04-29T11:39:17.1888692Z   Using cached charset_normalizer-3.4.7-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
2026-04-29T11:39:17.2003375Z Collecting idna<4,>=2.5 (from Requests==2.32.5->-r requirements.txt (line 9))
2026-04-29T11:39:17.2016130Z   Using cached idna-3.13-py3-none-any.whl.metadata (8.0 kB)
2026-04-29T11:39:17.2166529Z Collecting certifi>=2017.4.17 (from Requests==2.32.5->-r requirements.txt (line 9))
2026-04-29T11:39:17.2180310Z   Using cached certifi-2026.4.22-py3-none-any.whl.metadata (2.5 kB)
2026-04-29T11:39:17.2355132Z Collecting httpcore==1.* (from httpx<1,>=0.25.0->anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:17.2368465Z   Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
2026-04-29T11:39:17.2462356Z Collecting h11>=0.16 (from httpcore==1.*->httpx<1,>=0.25.0->anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:17.2475765Z   Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
2026-04-29T11:39:17.2555537Z Collecting annotated-types>=0.6.0 (from pydantic<3,>=1.9.0->anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:17.2569462Z   Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
2026-04-29T11:39:17.9163243Z Collecting pydantic-core==2.46.3 (from pydantic<3,>=1.9.0->anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:17.9184800Z   Using cached pydantic_core-2.46.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
2026-04-29T11:39:17.9266210Z Collecting typing-inspection>=0.4.2 (from pydantic<3,>=1.9.0->anthropic==0.84.0->-r requirements.txt (line 1))
2026-04-29T11:39:17.9280015Z   Using cached typing_inspection-0.4.2-py3-none-any.whl.metadata (2.6 kB)
2026-04-29T11:39:17.9528329Z Collecting google-auth<3.0.0,>=2.48.1 (from google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:17.9542046Z   Using cached google_auth-2.49.2-py3-none-any.whl.metadata (6.2 kB)
2026-04-29T11:39:17.9735902Z Collecting tenacity<9.2.0,>=8.2.3 (from google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:17.9749649Z   Using cached tenacity-9.1.4-py3-none-any.whl.metadata (1.2 kB)
2026-04-29T11:39:18.0475412Z Collecting websockets<17.0,>=13.0.0 (from google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.0490312Z   Using cached websockets-16.0-cp311-cp311-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl.metadata (6.8 kB)
2026-04-29T11:39:18.0642048Z Collecting pyasn1-modules>=0.2.1 (from google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.0655309Z   Using cached pyasn1_modules-0.4.2-py3-none-any.whl.metadata (3.5 kB)
2026-04-29T11:39:18.2252686Z Collecting cryptography>=38.0.3 (from google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.2267888Z   Using cached cryptography-47.0.0-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (4.5 kB)
2026-04-29T11:39:18.3655893Z Collecting cffi>=2.0.0 (from cryptography>=38.0.3->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.3672432Z   Using cached cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.6 kB)
2026-04-29T11:39:18.3752443Z Collecting pycparser (from cffi>=2.0.0->cryptography>=38.0.3->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.3765737Z   Using cached pycparser-3.0-py3-none-any.whl.metadata (8.2 kB)
2026-04-29T11:39:18.3931643Z Collecting pyasn1<0.7.0,>=0.6.1 (from pyasn1-modules>=0.2.1->google-auth<3.0.0,>=2.48.1->google-auth[requests]<3.0.0,>=2.48.1->google-genai>=0.8.0->-r requirements.txt (line 11))
2026-04-29T11:39:18.3945033Z   Using cached pyasn1-0.6.3-py3-none-any.whl.metadata (8.4 kB)
2026-04-29T11:39:18.4014238Z Using cached anthropic-0.84.0-py3-none-any.whl (455 kB)
2026-04-29T11:39:18.4029630Z Using cached feedparser-6.0.12-py3-none-any.whl (81 kB)
2026-04-29T11:39:18.4043360Z Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
2026-04-29T11:39:18.4057046Z Using cached markdown2-2.5.3-py3-none-any.whl (48 kB)
2026-04-29T11:39:18.4070930Z Using cached openai-2.28.0-py3-none-any.whl (1.1 MB)
2026-04-29T11:39:18.4088384Z Using cached openpyxl-3.1.5-py2.py3-none-any.whl (250 kB)
2026-04-29T11:39:18.4102667Z Using cached protobuf-7.34.0-cp310-abi3-manylinux2014_x86_64.whl (324 kB)
2026-04-29T11:39:18.4117003Z Using cached python_dotenv-1.2.2-py3-none-any.whl (22 kB)
2026-04-29T11:39:18.4130792Z Using cached requests-2.32.5-py3-none-any.whl (64 kB)
2026-04-29T11:39:18.4144280Z Using cached urllib3-2.6.3-py3-none-any.whl (131 kB)
2026-04-29T11:39:18.4157850Z Using cached anyio-4.13.0-py3-none-any.whl (114 kB)
2026-04-29T11:39:18.4172408Z Using cached charset_normalizer-3.4.7-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (214 kB)
2026-04-29T11:39:18.4186136Z Using cached distro-1.9.0-py3-none-any.whl (20 kB)
2026-04-29T11:39:18.4199932Z Using cached docstring_parser-0.18.0-py3-none-any.whl (22 kB)
2026-04-29T11:39:18.4213319Z Using cached httpx-0.28.1-py3-none-any.whl (73 kB)
2026-04-29T11:39:18.4226809Z Using cached httpcore-1.0.9-py3-none-any.whl (78 kB)
2026-04-29T11:39:18.4240597Z Using cached idna-3.13-py3-none-any.whl (68 kB)
2026-04-29T11:39:18.4254252Z Using cached jiter-0.14.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (358 kB)
2026-04-29T11:39:18.4268761Z Using cached pydantic-2.13.3-py3-none-any.whl (471 kB)
2026-04-29T11:39:18.4283837Z Using cached pydantic_core-2.46.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
2026-04-29T11:39:18.4304097Z Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
2026-04-29T11:39:18.4317613Z Using cached google_genai-1.73.1-py3-none-any.whl (783 kB)
2026-04-29T11:39:18.4333928Z Using cached google_auth-2.49.2-py3-none-any.whl (240 kB)
2026-04-29T11:39:18.4347789Z Using cached tenacity-9.1.4-py3-none-any.whl (28 kB)
2026-04-29T11:39:18.4361765Z Using cached websockets-16.0-cp311-cp311-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl (184 kB)
2026-04-29T11:39:18.4375395Z Using cached annotated_types-0.7.0-py3-none-any.whl (13 kB)
2026-04-29T11:39:18.4389741Z Using cached certifi-2026.4.22-py3-none-any.whl (135 kB)
2026-04-29T11:39:18.4403734Z Using cached cryptography-47.0.0-cp311-abi3-manylinux_2_34_x86_64.whl (4.7 MB)
2026-04-29T11:39:18.4433163Z Using cached cffi-2.0.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (215 kB)
2026-04-29T11:39:18.4446787Z Using cached h11-0.16.0-py3-none-any.whl (37 kB)
2026-04-29T11:39:18.4461020Z Using cached markupsafe-3.0.3-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
2026-04-29T11:39:18.4474353Z Using cached pyasn1_modules-0.4.2-py3-none-any.whl (181 kB)
2026-04-29T11:39:18.4488339Z Using cached pyasn1-0.6.3-py3-none-any.whl (83 kB)
2026-04-29T11:39:18.4501901Z Using cached tqdm-4.67.3-py3-none-any.whl (78 kB)
2026-04-29T11:39:18.4515598Z Using cached typing_inspection-0.4.2-py3-none-any.whl (14 kB)
2026-04-29T11:39:18.4529202Z Using cached et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
2026-04-29T11:39:18.4542561Z Using cached pycparser-3.0-py3-none-any.whl (48 kB)
2026-04-29T11:39:18.4555981Z Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
2026-04-29T11:39:18.5744380Z Installing collected packages: sgmllib3k, websockets, urllib3, typing-extensions, tqdm, tenacity, sniffio, python-dotenv, pycparser, pyasn1, protobuf, MarkupSafe, markdown2, jiter, idna, h11, feedparser, et-xmlfile, docstring-parser, distro, charset_normalizer, certifi, annotated-types, typing-inspection, Requests, pydantic-core, pyasn1-modules, openpyxl, Jinja2, httpcore, cffi, anyio, pydantic, httpx, cryptography, openai, google-auth, anthropic, google-genai
2026-04-29T11:39:22.1213259Z 
2026-04-29T11:39:22.1236675Z Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.3 Requests-2.32.5 annotated-types-0.7.0 anthropic-0.84.0 anyio-4.13.0 certifi-2026.4.22 cffi-2.0.0 charset_normalizer-3.4.7 cryptography-47.0.0 distro-1.9.0 docstring-parser-0.18.0 et-xmlfile-2.0.0 feedparser-6.0.12 google-auth-2.49.2 google-genai-1.73.1 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.13 jiter-0.14.0 markdown2-2.5.3 openai-2.28.0 openpyxl-3.1.5 protobuf-7.34.0 pyasn1-0.6.3 pyasn1-modules-0.4.2 pycparser-3.0 pydantic-2.13.3 pydantic-core-2.46.3 python-dotenv-1.2.2 sgmllib3k-1.0.0 sniffio-1.3.1 tenacity-9.1.4 tqdm-4.67.3 typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.6.3 websockets-16.0
2026-04-29T11:39:22.1268914Z 
2026-04-29T11:39:22.1269278Z [notice] A new release of pip is available: 26.0.1 -> 26.1
2026-04-29T11:39:22.1269956Z [notice] To update, run: pip install --upgrade pip
2026-04-29T11:39:22.4063554Z ##[group]Run python main.py
2026-04-29T11:39:22.4063859Z [36;1mpython main.py[0m
2026-04-29T11:39:22.4085319Z shell: /usr/bin/bash -e {0}
2026-04-29T11:39:22.4085566Z env:
2026-04-29T11:39:22.4085989Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:22.4086428Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:39:22.4086853Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:22.4087507Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:22.4087891Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:39:22.4088281Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:39:22.4088867Z   LLM_PROVIDER: ***
2026-04-29T11:39:22.4089170Z   GEMINI_API_KEY: ***
2026-04-29T11:39:22.4089383Z   ANTHROPIC_API_KEY: 
2026-04-29T11:39:22.4089629Z   OPENAI_API_KEY: ***
2026-04-29T11:39:22.4089884Z   RESEND_API_KEY: ***
2026-04-29T11:39:22.4090138Z   RECIPIENT_EMAIL: ***
2026-04-29T11:39:22.4090348Z ##[endgroup]
2026-04-29T11:39:22.4492835Z 2026-04-29 11:39:22,449 [INFO] main — ============================================================
2026-04-29T11:39:22.4493713Z 2026-04-29 11:39:22,449 [INFO] main — AI News Daily 시작
2026-04-29T11:39:22.4494527Z 2026-04-29 11:39:22,449 [INFO] main — ============================================================
2026-04-29T11:39:22.5468757Z 2026-04-29 11:39:22,546 [INFO] main — [1/5] 뉴스 수집 중...
2026-04-29T11:39:22.9570149Z 2026-04-29 11:39:22,956 [INFO] core.collector — [수집] 국내 경제 | 8건 ← https://www.hankyung.com/feed/economy
2026-04-29T11:39:26.7239714Z 2026-04-29 11:39:26,723 [WARNING] core.collector — [RSS 오류] https://www.edaily.co.kr/rss/rss_economy.xml — <unknown>:56:15: not well-formed (invalid token)
2026-04-29T11:39:27.8797345Z 2026-04-29 11:39:27,879 [WARNING] core.collector — [RSS 오류] https://biz.chosun.com/rss/rss.htm — <unknown>:28:85: not well-formed (invalid token)
2026-04-29T11:39:29.4215156Z 2026-04-29 11:39:29,421 [INFO] core.collector — [수집] 국내 경제 | 8건 ← https://www.mk.co.kr/rss/40300001/
2026-04-29T11:39:31.3812961Z 2026-04-29 11:39:31,380 [INFO] core.collector — [수집] 국내 경제 | 8건 ← https://news.einfomax.co.kr/rss/allArticle.xml
2026-04-29T11:39:32.3110596Z 2026-04-29 11:39:32,310 [INFO] core.collector — [수집] 국내 IT·기술 | 8건 ← https://rss.etnews.com/Section901.xml
2026-04-29T11:39:33.3396325Z 2026-04-29 11:39:33,339 [INFO] core.collector — [수집] 국내 IT·기술 | 8건 ← https://rss.etnews.com/04046.xml
2026-04-29T11:39:34.5413075Z 2026-04-29 11:39:34,540 [INFO] core.collector — [수집] 국내 IT·기술 | 8건 ← https://www.aitimes.com/rss/allArticle.xml
2026-04-29T11:39:36.6635698Z 2026-04-29 11:39:36,663 [WARNING] core.collector — [RSS 오류] https://zdnet.co.kr/rss/?t=a — <unknown>:29:4: undefined entity
2026-04-29T11:39:37.5083528Z 2026-04-29 11:39:37,508 [WARNING] core.collector — [RSS 오류] https://www.itworld.co.kr/rss/feed — <unknown>:34:0: undefined entity
2026-04-29T11:39:38.6741824Z 2026-04-29 11:39:38,673 [WARNING] core.collector — [RSS 오류] https://www.bloter.net/feed — <unknown>:2:0: syntax error
2026-04-29T11:39:40.3333126Z 2026-04-29 11:39:40,333 [WARNING] core.collector — [RSS 오류] https://www.aitimes.kr/rss/all.xml — <unknown>:2:0: syntax error
2026-04-29T11:39:40.7269961Z 2026-04-29 11:39:40,726 [INFO] core.collector — [수집] 글로벌 기술 | 8건 ← https://feeds.arstechnica.com/arstechnica/index
2026-04-29T11:39:41.1090484Z 2026-04-29 11:39:41,108 [INFO] core.collector — [수집] 글로벌 기술 | 8건 ← https://www.theverge.com/rss/index.xml
2026-04-29T11:39:41.4934661Z 2026-04-29 11:39:41,493 [INFO] core.collector — [수집] 글로벌 기술 | 8건 ← https://techcrunch.com/feed/
2026-04-29T11:39:42.0990681Z 2026-04-29 11:39:42,098 [WARNING] core.collector — [RSS 오류] https://feeds.wired.com/wired/index — text/html is not an XML media type
2026-04-29T11:39:42.5570315Z 2026-04-29 11:39:42,556 [INFO] core.collector — [수집] 글로벌 기술 | 8건 ← https://www.technologyreview.com/feed/
2026-04-29T11:39:43.0315302Z 2026-04-29 11:39:43,031 [INFO] core.collector — [수집] 글로벌 기술 | 8건 ← https://www.zdnet.com/news/rss.xml
2026-04-29T11:39:43.5456658Z 2026-04-29 11:39:43,545 [INFO] core.collector — [수집] AI·ML | 7건 ← https://venturebeat.com/category/ai/feed/
2026-04-29T11:39:44.0093219Z 2026-04-29 11:39:44,009 [WARNING] core.collector — [RSS 오류] https://www.artificialintelligence-news.com/feed/ — <unknown>:2:119: not well-formed (invalid token)
2026-04-29T11:39:44.6317519Z 2026-04-29 11:39:44,631 [INFO] core.collector — [수집] AI·ML | 8건 ← https://aiweekly.co/issues.rss
2026-04-29T11:39:45.0275908Z 2026-04-29 11:39:45,027 [WARNING] core.collector — [RSS 오류] https://www.deeplearning.ai/the-batch/feed/ — <unknown>:2:4391: not well-formed (invalid token)
2026-04-29T11:39:45.4501053Z 2026-04-29 11:39:45,449 [INFO] core.collector — [수집] AI·ML | 6건 ← https://www.technologyreview.com/topic/artificial-intelligence/feed/
2026-04-29T11:39:45.8353578Z 2026-04-29 11:39:45,835 [INFO] core.collector — [수집] AI·ML | 8건 ← https://www.wired.com/feed/tag/ai/la***/rss
2026-04-29T11:39:46.2153647Z 2026-04-29 11:39:46,215 [WARNING] core.collector — [RSS 오류] https://hai.stanford.edu/news/rss.xml — <unknown>:2:4358: not well-formed (invalid token)
2026-04-29T11:39:47.1089786Z 2026-04-29 11:39:47,108 [WARNING] core.collector — [RSS 오류] https://oecd.ai/en/news-and-blog/feed — <unknown>:2635:11: mismatched tag
2026-04-29T11:39:47.4094731Z 2026-04-29 11:39:47,409 [INFO] core.collector — [수집 완료] 총 117건 (EN:69 KO:46) 키워드:2건 → AI 40건
2026-04-29T11:39:47.4099667Z 2026-04-29 11:39:47,409 [INFO] main —      → 총 117건 수집 (EN:69 KO:46) | 키워드:2건 | 중복 제외:0건
2026-04-29T11:39:48.8847594Z 2026-04-29 11:39:48,884 [INFO] main — [2/5] AI 분석 중...
2026-04-29T11:39:48.9376464Z 2026-04-29 11:39:48,937 [INFO] core.analyzer — [모델 선택] ***-3.1-flash-lite-preview (뉴스 69건, 기준 40건)
2026-04-29T11:39:48.9377733Z 2026-04-29 11:39:48,937 [INFO] google_genai.models — AFC is enabled with max remote calls: 10.
2026-04-29T11:40:01.6407937Z 2026-04-29 11:40:01,640 [INFO] httpx — HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/***-3.1-flash-lite-preview:generateContent "HTTP/1.1 200 OK"
2026-04-29T11:40:01.6419384Z 2026-04-29 11:40:01,641 [INFO] core.analyzer — [Gemini 분석 완료] 영어 69건
2026-04-29T11:40:01.6420779Z 2026-04-29 11:40:01,641 [INFO] core.analyzer — [모델 선택] ***-3.1-flash-lite-preview (뉴스 46건, 기준 40건)
2026-04-29T11:40:01.6422061Z 2026-04-29 11:40:01,642 [INFO] google_genai.models — AFC is enabled with max remote calls: 10.
2026-04-29T11:40:03.4060168Z 2026-04-29 11:40:03,405 [INFO] httpx — HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/***-3.1-flash-lite-preview:generateContent "HTTP/1.1 503 Service Unavailable"
2026-04-29T11:40:03.4067693Z 2026-04-29 11:40:03,406 [ERROR] core.analyzer — [Gemini KO 실패] 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}
2026-04-29T11:40:03.4071578Z 2026-04-29 11:40:03,406 [INFO] main —      → 분석 완료
2026-04-29T11:40:03.4269863Z 2026-04-29 11:40:03,426 [INFO] main — [3/5] 리포트 생성 중...
2026-04-29T11:40:03.4331489Z 2026-04-29 11:40:03,432 [INFO] core.report — [리포트 저장] reports/news_2026-04-29.md
2026-04-29T11:40:03.4332525Z 2026-04-29 11:40:03,433 [INFO] main —      → 저장: reports/news_2026-04-29.md
2026-04-29T11:40:03.5756881Z 2026-04-29 11:40:03,575 [INFO] main — [4/5] DB 누적 저장 중...
2026-04-29T11:40:03.9918572Z 2026-04-29 11:40:03,991 [INFO] core.db — [DB 저장] 117건 추가 → storage/news_db.xlsx
2026-04-29T11:40:03.9919490Z 2026-04-29 11:40:03,991 [INFO] main —      → 117건 저장 완료
2026-04-29T11:40:04.0027330Z 2026-04-29 11:40:04,002 [INFO] main — [5/5] 이메일 발송 중...
2026-04-29T11:40:04.3094786Z 2026-04-29 11:40:04,309 [INFO] core.mailer — [이메일 발송] 성공 → ['***']
2026-04-29T11:40:04.3104702Z 2026-04-29 11:40:04,310 [INFO] main —      → 성공
2026-04-29T11:40:04.3105540Z 2026-04-29 11:40:04,310 [INFO] main — ============================================================
2026-04-29T11:40:04.3106385Z 2026-04-29 11:40:04,310 [INFO] main — 완료! 소요 시간: 41초
2026-04-29T11:40:04.3107901Z 2026-04-29 11:40:04,310 [INFO] main — ============================================================
2026-04-29T11:40:04.4459791Z ##[group]Run python scripts/build_site.py
2026-04-29T11:40:04.4460163Z [36;1mpython scripts/build_site.py[0m
2026-04-29T11:40:04.4481833Z shell: /usr/bin/bash -e {0}
2026-04-29T11:40:04.4482088Z env:
2026-04-29T11:40:04.4482358Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:04.4482803Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:04.4483227Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:04.4483604Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:04.4483976Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:04.4484359Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:04.4484677Z ##[endgroup]
2026-04-29T11:40:05.1407557Z   ✓ 2026-04-29.html
2026-04-29T11:40:05.1408166Z   ✓ 2026-04-27.html
2026-04-29T11:40:05.1408651Z   ✓ 2026-04-26.html
2026-04-29T11:40:05.1409190Z   ✓ 2026-04-25.html
2026-04-29T11:40:05.1409770Z   ✓ 2026-04-24.html
2026-04-29T11:40:05.1410225Z   ✓ 2026-04-23.html
2026-04-29T11:40:05.1410692Z   ✓ 2026-04-22.html
2026-04-29T11:40:05.1411133Z   ✓ 2026-04-21.html
2026-04-29T11:40:05.1411576Z   ✓ 2026-04-20.html
2026-04-29T11:40:05.1412005Z   ✓ 2026-04-19.html
2026-04-29T11:40:05.1412328Z   ✓ 2026-04-18.html
2026-04-29T11:40:05.1412536Z   ✓ 2026-04-17.html
2026-04-29T11:40:05.1412739Z   ✓ 2026-04-16.html
2026-04-29T11:40:05.1412948Z   ✓ 2026-04-15.html
2026-04-29T11:40:05.1413158Z   ✓ 2026-04-14.html
2026-04-29T11:40:05.1413364Z   ✓ 2026-04-13.html
2026-04-29T11:40:05.1413567Z   ✓ 2026-04-12.html
2026-04-29T11:40:05.1413767Z   ✓ 2026-04-11.html
2026-04-29T11:40:05.1431334Z   ✓ 2026-04-10.html
2026-04-29T11:40:05.1431814Z   ✓ 2026-04-09.html
2026-04-29T11:40:05.1432185Z   ✓ 2026-04-08.html
2026-04-29T11:40:05.1432502Z   ✓ 2026-04-07.html
2026-04-29T11:40:05.1432726Z   ✓ 2026-04-06.html
2026-04-29T11:40:05.1432945Z   ✓ 2026-04-05.html
2026-04-29T11:40:05.1433156Z   ✓ 2026-04-04.html
2026-04-29T11:40:05.1433371Z   ✓ 2026-04-03.html
2026-04-29T11:40:05.1433579Z   ✓ 2026-04-02.html
2026-04-29T11:40:05.1433800Z   ✓ 2026-04-01.html
2026-04-29T11:40:05.1434004Z   ✓ 2026-03-31.html
2026-04-29T11:40:05.1434205Z   ✓ 2026-03-30.html
2026-04-29T11:40:05.1434406Z   ✓ 2026-03-29.html
2026-04-29T11:40:05.1434605Z   ✓ 2026-03-28.html
2026-04-29T11:40:05.1434805Z   ✓ 2026-03-27.html
2026-04-29T11:40:05.1435029Z   ✓ 2026-03-26.html
2026-04-29T11:40:05.1435232Z   ✓ 2026-03-25.html
2026-04-29T11:40:05.1435433Z   ✓ 2026-03-24.html
2026-04-29T11:40:05.1435633Z   ✓ 2026-03-23.html
2026-04-29T11:40:05.1435837Z   ✓ 2026-03-22.html
2026-04-29T11:40:05.1436039Z   ✓ 2026-03-21.html
2026-04-29T11:40:05.1436237Z   ✓ 2026-03-20.html
2026-04-29T11:40:05.1436438Z   ✓ 2026-03-19.html
2026-04-29T11:40:05.1436639Z   ✓ 2026-03-18.html
2026-04-29T11:40:05.1436840Z   ✓ 2026-03-17.html
2026-04-29T11:40:05.1437307Z   ✓ 2026-03-16.html
2026-04-29T11:40:05.1437518Z   ✓ 2026-03-15.html
2026-04-29T11:40:05.1437733Z   ✓ 2026-03-14.html
2026-04-29T11:40:05.1437936Z   ✓ 2026-03-12.html
2026-04-29T11:40:05.1438138Z   ✓ 2026-03-11.html
2026-04-29T11:40:05.1438348Z   ✓ 2026-03-10.html
2026-04-29T11:40:05.1438614Z   ✓ reports-data.json (49개 리포트)
2026-04-29T11:40:05.1438794Z 
2026-04-29T11:40:05.1438931Z ✅ 49개 리포트 빌드 완료 → publish/
2026-04-29T11:40:05.1439186Z    최신: 2026-04-29
2026-04-29T11:40:05.1518966Z ##[group]Run git config user.name  "github-actions[bot]"
2026-04-29T11:40:05.1519414Z [36;1mgit config user.name  "github-actions[bot]"[0m
2026-04-29T11:40:05.1519768Z [36;1mgit config user.email "actions@github.com"[0m
2026-04-29T11:40:05.1520082Z [36;1mgit add reports/ publish/ storage/[0m
2026-04-29T11:40:05.1520378Z [36;1mgit diff --staged --quiet || \[0m
2026-04-29T11:40:05.1520713Z [36;1m  git commit -m "📰 Daily report $(date +'%Y-%m-%d')"[0m
2026-04-29T11:40:05.1521031Z [36;1mgit push[0m
2026-04-29T11:40:05.1542124Z shell: /usr/bin/bash -e {0}
2026-04-29T11:40:05.1542372Z env:
2026-04-29T11:40:05.1542634Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:05.1543078Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:05.1543781Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:05.1544164Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:05.1544663Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:05.1545249Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:05.1545590Z ##[endgroup]
2026-04-29T11:40:05.2326544Z [main 326fa0f] 📰 Daily report 2026-04-29
2026-04-29T11:40:05.2327219Z  54 files changed, 617 insertions(+), 279 deletions(-)
2026-04-29T11:40:06.5409958Z To https://github.com/chamgil71/dailynews
2026-04-29T11:40:06.5410505Z    60e0e7f..326fa0f  main -> main
2026-04-29T11:40:06.5604217Z ##[group]Run actions/upload-pages-artifact@v3
2026-04-29T11:40:06.5604553Z with:
2026-04-29T11:40:06.5604750Z   path: publish/
2026-04-29T11:40:06.5604970Z   name: github-pages
2026-04-29T11:40:06.5605193Z   retention-days: 1
2026-04-29T11:40:06.5605390Z env:
2026-04-29T11:40:06.5605664Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5606094Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:06.5606513Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5606890Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5607610Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5608003Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:06.5608322Z ##[endgroup]
2026-04-29T11:40:06.5682968Z ##[group]Run echo ::group::Archive artifact
2026-04-29T11:40:06.5683288Z [36;1mecho ::group::Archive artifact[0m
2026-04-29T11:40:06.5683569Z [36;1mtar \[0m
2026-04-29T11:40:06.5683802Z [36;1m  --dereference --hard-dereference \[0m
2026-04-29T11:40:06.5684101Z [36;1m  --directory "$INPUT_PATH" \[0m
2026-04-29T11:40:06.5684400Z [36;1m  -cvf "$RUNNER_TEMP/artifact.tar" \[0m
2026-04-29T11:40:06.5684684Z [36;1m  --exclude=.git \[0m
2026-04-29T11:40:06.5684924Z [36;1m  --exclude=.github \[0m
2026-04-29T11:40:06.5685150Z [36;1m  .[0m
2026-04-29T11:40:06.5685342Z [36;1mecho ::endgroup::[0m
2026-04-29T11:40:06.5726138Z shell: /usr/bin/sh -e {0}
2026-04-29T11:40:06.5726516Z env:
2026-04-29T11:40:06.5727137Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5727866Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:06.5728572Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5729208Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5729794Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5730379Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:06.5730900Z   INPUT_PATH: publish/
2026-04-29T11:40:06.5731233Z ##[endgroup]
2026-04-29T11:40:06.5788703Z ##[group]Archive artifact
2026-04-29T11:40:06.5805046Z ./
2026-04-29T11:40:06.5805399Z ./2026-04-07.html
2026-04-29T11:40:06.5805755Z ./2026-04-21.html
2026-04-29T11:40:06.5806101Z ./2026-03-10.html
2026-04-29T11:40:06.5806436Z ./2026-04-22.html
2026-04-29T11:40:06.5806766Z ./2026-04-01.html
2026-04-29T11:40:06.5807344Z ./2026-04-18.html
2026-04-29T11:40:06.5807683Z ./2026-03-18.html
2026-04-29T11:40:06.5808008Z ./2026-04-11.html
2026-04-29T11:40:06.5808342Z ./2026-03-25.html
2026-04-29T11:40:06.5808676Z ./2026-03-27.html
2026-04-29T11:40:06.5809005Z ./2026-04-04.html
2026-04-29T11:40:06.5809333Z ./2026-03-15.html
2026-04-29T11:40:06.5809670Z ./2026-04-14.html
2026-04-29T11:40:06.5809999Z ./index.html
2026-04-29T11:40:06.5810328Z ./2026-03-20.html
2026-04-29T11:40:06.5810690Z ./reports-data.json
2026-04-29T11:40:06.5820182Z ./2026-04-27.html
2026-04-29T11:40:06.5820550Z ./2026-03-21.html
2026-04-29T11:40:06.5820883Z ./2026-04-12.html
2026-04-29T11:40:06.5821221Z ./2026-03-14.html
2026-04-29T11:40:06.5821543Z ./2026-03-19.html
2026-04-29T11:40:06.5821870Z ./2026-04-15.html
2026-04-29T11:40:06.5822424Z ./2026-03-26.html
2026-04-29T11:40:06.5822767Z ./archive.html
2026-04-29T11:40:06.5823115Z ./2026-04-19.html
2026-04-29T11:40:06.5823443Z ./2026-03-28.html
2026-04-29T11:40:06.5823784Z ./app.html
2026-04-29T11:40:06.5824108Z ./2026-04-17.html
2026-04-29T11:40:06.5824448Z ./2026-03-31.html
2026-04-29T11:40:06.5824776Z ./2026-03-17.html
2026-04-29T11:40:06.5825108Z ./2026-03-29.html
2026-04-29T11:40:06.5825451Z ./2026-04-08.html
2026-04-29T11:40:06.5825779Z ./2026-03-22.html
2026-04-29T11:40:06.5826102Z ./2026-04-20.html
2026-04-29T11:40:06.5826431Z ./2026-03-12.html
2026-04-29T11:40:06.5826752Z ./2026-04-23.html
2026-04-29T11:40:06.5827275Z ./2026-03-11.html
2026-04-29T11:40:06.5827835Z ./reports.json
2026-04-29T11:40:06.5828205Z ./2026-04-10.html
2026-04-29T11:40:06.5828543Z ./2026-03-24.html
2026-04-29T11:40:06.5828878Z ./2026-04-25.html
2026-04-29T11:40:06.5829213Z ./2026-04-26.html
2026-04-29T11:40:06.5829540Z ./2026-04-03.html
2026-04-29T11:40:06.5829868Z ./2026-04-09.html
2026-04-29T11:40:06.5830211Z ./2026-04-29.html
2026-04-29T11:40:06.5830526Z ./2026-03-23.html
2026-04-29T11:40:06.5830857Z ./2026-04-24.html
2026-04-29T11:40:06.5831181Z ./2026-04-16.html
2026-04-29T11:40:06.5831503Z ./2026-04-02.html
2026-04-29T11:40:06.5831828Z ./2026-04-05.html
2026-04-29T11:40:06.5832149Z ./2026-03-16.html
2026-04-29T11:40:06.5832473Z ./2026-04-13.html
2026-04-29T11:40:06.5832804Z ./2026-03-30.html
2026-04-29T11:40:06.5833116Z ./2026-04-06.html
2026-04-29T11:40:06.5835921Z ##[endgroup]
2026-04-29T11:40:06.5906360Z ##[group]Run actions/upload-artifact@v4
2026-04-29T11:40:06.5906634Z with:
2026-04-29T11:40:06.5906821Z   name: github-pages
2026-04-29T11:40:06.5907322Z   path: /home/runner/work/_temp/artifact.tar
2026-04-29T11:40:06.5907602Z   retention-days: 1
2026-04-29T11:40:06.5907811Z   if-no-files-found: error
2026-04-29T11:40:06.5908038Z   compression-level: 6
2026-04-29T11:40:06.5908246Z   overwrite: false
2026-04-29T11:40:06.5908453Z   include-hidden-files: false
2026-04-29T11:40:06.5908674Z env:
2026-04-29T11:40:06.5908919Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5909338Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:06.5909751Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5910121Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5910490Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:06.5910860Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:06.5911169Z ##[endgroup]
2026-04-29T11:40:06.8142760Z With the provided path, there will be 1 file uploaded
2026-04-29T11:40:06.8149060Z Artifact name is valid!
2026-04-29T11:40:06.8150334Z Root directory input is valid!
2026-04-29T11:40:07.1312715Z Beginning upload of artifact content to blob storage
2026-04-29T11:40:07.6996535Z Uploaded bytes 398611
2026-04-29T11:40:07.7737376Z Finished uploading artifact content to blob storage!
2026-04-29T11:40:07.7741428Z SHA256 digest of uploaded artifact zip is 5ccaa2f38eae5f910459bff972fbcc64d87d78174c33f6ce5bef5f67be55d3a4
2026-04-29T11:40:07.7743174Z Finalizing artifact upload
2026-04-29T11:40:08.0124268Z Artifact github-pages.zip successfully finalized. Artifact ID 6706175563
2026-04-29T11:40:08.0125681Z Artifact github-pages has been successfully uploaded! Final size is 398611 bytes. Artifact ID is 6706175563
2026-04-29T11:40:08.0132799Z Artifact download URL: https://github.com/chamgil71/dailynews/actions/runs/25106673800/artifacts/6706175563
2026-04-29T11:40:08.0284801Z ##[group]Run actions/deploy-pages@v4
2026-04-29T11:40:08.0285104Z with:
2026-04-29T11:40:08.0285411Z   token: ***
2026-04-29T11:40:08.0285604Z   timeout: 600000
2026-04-29T11:40:08.0285802Z   error_count: 10
2026-04-29T11:40:08.0286008Z   reporting_interval: 5000
2026-04-29T11:40:08.0286256Z   artifact_name: github-pages
2026-04-29T11:40:08.0286499Z   preview: false
2026-04-29T11:40:08.0286690Z env:
2026-04-29T11:40:08.0287312Z   pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:08.0288002Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
2026-04-29T11:40:08.0288442Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:08.0288836Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:08.0289228Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
2026-04-29T11:40:08.0289611Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
2026-04-29T11:40:08.0289931Z ##[endgroup]
2026-04-29T11:40:08.5461895Z Fetching artifact metadata for "github-pages" in this workflow run
2026-04-29T11:40:08.8142043Z Found 1 artifact(s)
2026-04-29T11:40:08.8156126Z Creating Pages deployment with payload:
2026-04-29T11:40:08.8156835Z {
2026-04-29T11:40:08.8157485Z 	"artifact_id": 6706175563,
2026-04-29T11:40:08.8158003Z 	"pages_build_version": "60e0e7f7949f7e965cda62a9f5db0791b2665807",
2026-04-29T11:40:08.8192182Z 	"oidc_token": "***"
2026-04-29T11:40:08.8202025Z }
2026-04-29T11:40:09.2482609Z Created deployment for 60e0e7f7949f7e965cda62a9f5db0791b2665807, ID: 60e0e7f7949f7e965cda62a9f5db0791b2665807
2026-04-29T11:40:14.2506177Z Getting Pages deployment status...
2026-04-29T11:40:14.4895858Z Reported success!
2026-04-29T11:40:14.5075074Z Post job cleanup.
2026-04-29T11:40:14.6586779Z Cache hit occurred on the primary key setup-python-Linux-x64-24.04-Ubuntu-python-3.11.15-pip-cc177e0a319e2b366e42ffbff4d20b32e7f9f00ab75eb7e3434e6f9155173566, not saving cache.
2026-04-29T11:40:14.6688795Z Post job cleanup.
2026-04-29T11:40:14.7631269Z [command]/usr/bin/git version
2026-04-29T11:40:14.7668357Z git version 2.53.0
2026-04-29T11:40:14.7712404Z Temporarily overriding HOME='/home/runner/work/_temp/c6fcefeb-2d2e-49f8-939c-ce61fdf6f4a7' before making global git config changes
2026-04-29T11:40:14.7713798Z Adding repository directory to the temporary git global config as a safe directory
2026-04-29T11:40:14.7725964Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/dailynews/dailynews
2026-04-29T11:40:14.7759853Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-04-29T11:40:14.7791613Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-04-29T11:40:14.8014216Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-04-29T11:40:14.8034601Z http.https://github.com/.extraheader
2026-04-29T11:40:14.8046674Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-04-29T11:40:14.8076312Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-04-29T11:40:14.8293833Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-04-29T11:40:14.8323803Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-04-29T11:40:14.8646173Z Evaluate and set environment url
2026-04-29T11:40:14.8649933Z Evaluated environment url: https://chamgil71.github.io/dailynews/
2026-04-29T11:40:14.8650858Z Cleaning up orphan processes
2026-04-29T11:40:14.8932166Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/deploy-pages@v4, actions/setup-python@v5, actions/upload-artifact@v4. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
