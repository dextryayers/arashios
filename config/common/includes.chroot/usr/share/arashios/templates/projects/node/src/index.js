export const VERSION = "0.1.0";

export function greet(name = "ArashiOS") {
  return `Halo ${name} dari @NAME@`;
}

if (process.argv[1]?.endsWith("index.js")) {
  console.log(greet());
}
