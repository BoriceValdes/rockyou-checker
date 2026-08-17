import js from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";

const tsRules = {
  files: ["**/*.{ts,tsx}"],
  languageOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    parser: tsParser,
  },
  plugins: {
    "@typescript-eslint": tseslint,
    "react-hooks": reactHooks,
    "react-refresh": reactRefresh,
  },
  rules: {
    ...tseslint.configs.recommended.rules,
    ...reactHooks.configs.recommended.rules,
    "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
  },
};

export default [
  { ignores: ["dist/**"] },
  js.configs.recommended,
  {
    // Code applicatif : exécuté dans le navigateur.
    ...tsRules,
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: { ...tsRules.languageOptions, globals: globals.browser },
  },
  {
    // Fichiers de configuration à la racine : exécutés par Node (Vite, etc.).
    ...tsRules,
    files: ["*.ts"],
    languageOptions: { ...tsRules.languageOptions, globals: globals.node },
  },
];
