const express = require("express");

const app = express();
app.get("/ready", (_request, response) => response.json({ ready: true }));
app.listen(3000);
