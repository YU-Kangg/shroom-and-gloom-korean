# 소스 빌드와 1차 배포

일반 설치에는 소스 빌드가 필요하지 않습니다. `README.md`의 설치 ZIP을 사용하세요.

## 번역만 수정

Python 3.12 이상에서 `python tools/build_catalog.py`를 실행합니다. 원문 텍스트 없이 공개된 키·해시·토큰 규칙으로 검사하고 배포 JSON을 생성합니다. `translations/upstream.json`은 출처 확인용이며 빌드에 병합하지 않습니다.

## 플러그인과 ZIP 빌드

Windows PowerShell에서 저장소 루트를 기준으로 실행합니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/bootstrap-tools.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -BepInExRoot 'C:\게임경로\BepInEx' -Package
```

부트스트랩은 해시가 고정된 Python 3.12.10, .NET SDK 8.0.425, 공식 BepInEx 755를 `.work/`에 받습니다. 시스템 설정은 변경하지 않습니다. `BepInExRoot`는 소유한 게임에 BepInEx를 설치하고 한 번 실행하여 **현재 버전의** `interop/`이 생성된 경로입니다. 데모용 interop DLL로 빌드하지 마세요. NuGet 복원과 첫 다운로드에는 인터넷이 필요합니다.

`dist/`에 설치 ZIP, 소스 ZIP, `SHA256SUMS.txt`, 패키지 검사 보고서가 생성됩니다. 공식 로더와 한국어 플러그인·번역·글꼴만 지정한 경로에서 모으며, 게임 디렉터리 전체를 압축하지 않습니다. LGPL 라이브러리의 대응 소스 ZIP도 설치 ZIP에 동봉합니다.

## 새로운 게임 버전 검토

`tools/inspect_assets.py`와 `tools/catalog.py`는 저장소가 게임 폴더 안에 있을 때 소유한 게임의 영어 테이블을 `.work/inventory/`로 읽습니다. UnityPy 1.25.3이 필요합니다. `catalog.py`의 기존 데모 번역 후보 읽기는 선택 사항입니다. 추출 결과에는 원문이 있으므로 커밋하지 마세요.

새 원문과 기존 번역을 비교·교정한 뒤에만 `tools/export_schema.py`로 키·해시·토큰 구조를 갱신합니다. 해시만 바꾸면 오래된 번역을 새 버전에 억지로 적용할 수 있으므로 문구 검토 없이 실행하지 마세요. `preserved.json`의 해시가 바뀌어도 개별 검토가 필요합니다.

## 글꼴 재생성

일반 빌드는 이미 생성된 `assets/shroom-korean-jua`를 사용합니다. 재생성 도구는 `tools/build_font.py`이며 UnityPy 1.25.3, Pillow 12.3.0, fonttools 4.65.0, freetype-py 2.5.1, scipy 1.18.1, numpy 2.5.3을 사용했습니다. 템플릿은 데모 패치 v1.0.0의 `hakgyoansimnadeuri`를 `.work/upstream-package/`에 준비합니다. 글꼴 원본과 OFL 사본은 저장소에 포함되어 있습니다.

## GitHub 첫 배포

1. 빈 공개 저장소를 만들고 소스 ZIP의 **내용물**을 저장소 루트에 업로드합니다. `.work/`, 게임 폴더 전체, 로그와 interop DLL은 업로드하지 않습니다.
2. 릴리스 버전 태그로 **Pre-release**를 만듭니다. 제목과 본문에는 `RELEASE_NOTES.md`를 사용합니다.
3. 설치 ZIP 하나만 릴리스 첨부 파일로 올립니다. GitHub가 자동 생성하는 Source code ZIP과 TAR은 설치 파일이 아니라고 안내합니다.
4. 공개 페이지에서 설치 ZIP을 다시 받아 파일 해시와 설치 구조를 확인합니다.

실제 게시에는 게시할 GitHub 계정·저장소와 인증이 필요합니다. 로컬 패키지 생성만으로 GitHub에 게시되지는 않습니다.
