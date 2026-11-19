import React from "react";
import { createRoot } from "react-dom/client";
import App from "../src/app/App.tsx";
import "../src/styles/global.css";
import { install } from "./m5-iwer-fixture.js";

window.iwer = install(window.iwerOptions);
const root = createRoot(document.getElementById("root"));
window.unmountVisitor = () => root.unmount();
root.render(React.createElement(App));
