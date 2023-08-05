# Apache-airflow-providers-fxiaoke

Airflow plugin for [fxiaoke API](https://open.fxiaoke.com/wiki.html)

## Install

```bash
pip install airflow-providers-fxiaoke
```

## Usage

Create New connections named `fxiaoke_default` with extra json:
`{"app_id":"", "app_secret":"", "permanent_code":"", "open_user_id":""}`

### Hooks

- FxiaokeHooks


### Operators

- FxiaokeToGCSOperator
