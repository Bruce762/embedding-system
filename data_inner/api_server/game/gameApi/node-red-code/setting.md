# 要設定的

要到 `~/.node-red/settings.js`設定路徑

```js
const path = require("path");           // ← 新增（若之前加過可跳過）

module.exports = {
// ← 修改
httpStatic: "/Users/wangguanzhe/Desktop/code/embedded_system/data_inner/api_server/game/gameApi/media",   
```
