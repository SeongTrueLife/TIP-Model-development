# 백업 가이드 (Version History)

## 📦 백업 파일 네이밍 규칙

```
backup_model3_v[버전]_[날짜]_[시간].zip
```

**예시:**
- `backup_model3_v7.8.1_20260211_1325.zip`
  - 버전: v7.8.1
  - 날짜: 2026년 02월 11일
  - 시간: 13:25

---

## 🔧 새 백업 만드는 방법

### PowerShell 명령어:
```powershell
# 현재 시간을 변수로 저장
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$version = "v7.8.1"  # 버전 변경 시 수정

# 백업 생성 (이전 파일 유지)
Get-ChildItem -Path . -Exclude "backup_*.zip","venv","__pycache__" | 
  Compress-Archive -DestinationPath ".\backup_model3_${version}_${timestamp}.zip" -Force
```

---

## 📋 현재 백업 버전 히스토리

| 버전 | 날짜 | 주요 변경사항 |
|------|------|--------------|
| v7.8.1 | 2026-02-11 13:25 | JSON 파싱 에러 수정 (3단계 Fallback) |
| v7.8.0 | 2026-02-11 13:00 | The Rule, venv 설정 가이드 추가 |

---

## 🗑️ 백업 정리 가이드

**권장:** 최근 3~5개 버전만 유지

```powershell
# 오래된 백업 삭제 (예: 7일 이상 된 파일)
Get-ChildItem -Filter "backup_*.zip" | 
  Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | 
  Remove-Item
```
