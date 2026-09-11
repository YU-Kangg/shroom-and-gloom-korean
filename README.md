# Shroom and Gloom 얼리 액세스 한국어 패치

Windows Steam **0.6.21 / 빌드 25221077**용 비공식 유저 한글화입니다. 첫 공개 버전은 **v0.1.0-beta.1**입니다.

카드 이름뿐 아니라 효과, 키워드에 마우스를 올렸을 때의 설명, 적, 대화와 UI를 번역합니다. 단일 대상 피해는 **‘대상에게 5 피해’**, 전체 공격은 **‘모든 적에게 5 피해’**처럼 표시합니다. 번역 문구 2,735개를 수록했으며, 제작진 이름·기호·의도적인 글자 깨짐 연출 등 77개는 원문을 유지합니다. 모든 카드 조합과 후반 이벤트를 실기 검증한 것은 아닙니다.

## 설치

1. 게임을 종료합니다. 다른 한글 패치나 모드를 사용 중이라면 해당 파일을 먼저 별도 보관합니다. 데모용 XUnity 패치와 함께 설치하지 마세요.
2. Releases에서 `ShroomAndGloom-Korean-v0.1.0-beta.1-win-x64.zip`을 받습니다. GitHub의 `Source code (zip)`은 설치 파일이 아닙니다.
3. Steam 라이브러리 → 게임 우클릭 → 관리 → 로컬 파일 탐색을 엽니다.
4. ZIP **안의 내용물**을 `Shroom and Gloom.exe`가 있는 폴더에 복사합니다. `winhttp.dll`과 게임 실행 파일이 같은 위치에 있어야 합니다.
5. 게임을 실행하고 언어를 **English**로 설정합니다. 영어 문자열에 한국어 번역을 적용하는 방식입니다.

첫 실행은 로더가 필요한 Unity 라이브러리를 내려받고 현재 게임용 캐시를 만들기 때문에 인터넷 연결이 필요하며 수 분 걸릴 수 있습니다. 이후 실행에는 별도의 번역 서비스가 필요하지 않습니다. 일반 사용자는 Python이나 .NET SDK를 설치할 필요가 없습니다.

```text
Shroom and Gloom.exe
winhttp.dll
doorstop_config.ini
dotnet/
BepInEx/
  core/
  config/BepInEx.cfg
  plugins/ShroomKorean/
    ShroomKorean.dll
    translations.json
    shroom-korean-jua
ShroomKorean-docs/
```

## 업데이트와 제거

패치를 교체한 뒤에는 게임을 완전히 종료하고 다시 실행해야 합니다. 실행 중인 게임은 기존 번역을 계속 사용합니다.

한국어 패치만 끄려면 `BepInEx/plugins/ShroomKorean` 폴더를 게임 밖으로 옮기세요. 이 패치만 설치했다면 설치 ZIP에 포함된 로더 파일도 제거할 수 있습니다. 다른 모드가 사용하는 `BepInEx`, `dotnet`, `winhttp.dll`을 함께 지우지 않도록 주의하세요. 원본 게임 데이터와 저장 파일은 이 패치가 수정하지 않습니다.

게임 업데이트로 원문이 바뀐 항목은 해시 검증에 따라 번역을 건너뛰고 원문을 표시합니다. 게임의 내부 API가 바뀌면 패치 자체의 업데이트가 필요할 수도 있습니다. 다른 게임 버전에서의 정상 작동을 보장하지 않습니다.

## 글꼴과 번역

원래 영문 글꼴은 유지하고, 둥글고 두꺼운 손글씨 분위기의 **배달의민족 주아체(Jua)**를 한국어 보조 글꼴로 사용합니다. 주아체에 없는 한글 음절은 **Noto Sans KR**로 보완했습니다. 현대 한글 11,172자를 포함한 SDF 글꼴을 수록합니다.

용어는 [GLOSSARY.md](GLOSSARY.md), 검증 범위와 알려진 문제는 [TESTING.md](TESTING.md)를 참고하세요. 잘못된 번역을 제보할 때는 카드 이름, 화면의 문장, 게임 버전을 적어 주세요. 로그나 스크린샷을 공개할 때 계정·세션 식별자는 지워 주세요.

## 직접 수정하기

`translations/`의 표별 JSON을 수정하고 Python 3.12에서 다음 명령을 실행합니다.

```powershell
python tools/build_catalog.py
```

검사를 통과하면 `artifacts/translations.json`이 생성됩니다. 이를 `BepInEx/plugins/ShroomKorean/translations.json`에 복사하고 게임을 재시작하세요. 대괄호 안의 토큰과 `<link=...>`의 ID는 게임이 사용하는 값이므로 유지해야 합니다. 카드 참조 링크의 표시 이름은 카드 이름 번역과 일치해야 합니다.

DLL 빌드와 배포 ZIP 생성은 [BUILDING.md](BUILDING.md)를 참고하세요. 공개 저장소에는 원본 게임 실행 파일, 데이터 번들, 게임에서 생성한 interop DLL, 저장 파일을 넣지 않습니다.

## 원작·기여·라이선스

원작 게임의 권리는 해당 권리자에게 있습니다. 공식 한국어 지원이나 개발사의 공식 배포물이 아닙니다.

[oatone-textcat의 데모 한국어 패치](https://github.com/oatone-textcat/shroom-and-gloom-demo-korean)를 참고했으며, 번역 일부를 계승·교정하고 얼리 액세스의 새 문구를 번역했습니다. 참조 커밋은 `5f5e1001d9ed34c43334ea5bf97c847db2246e5b`입니다. 해당 패치의 글꼴 번들을 직렬화 템플릿으로 사용하고 글리프·아틀라스·글꼴 정보를 새로 생성했습니다. 기존 데모용 번역 플러그인은 배포하지 않습니다.

번역과 위 템플릿 기반 번들의 이용 조건은 **CC BY-NC-SA 4.0**입니다. 새로 작성한 플러그인·도구 코드는 **MIT**, 글꼴 원본은 **SIL OFL 1.1**입니다. 로더와 구성 라이브러리는 각각의 라이선스를 따릅니다. 자세한 출처와 사본은 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)와 `licenses/`를 참고하세요.
