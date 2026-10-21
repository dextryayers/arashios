import test from "node:test";
import assert from "node:assert/strict";
import { greet } from "../src/index.js";

test("greet menyapa", () => {
  assert.equal(greet("Kage"), "Halo Kage dari @NAME@");
});
