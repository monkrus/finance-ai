import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // Generated artifacts that must not be linted:
    "coverage/**",
  ]),
  {
    // CommonJS config files legitimately use require().
    files: ["*.config.js", "jest.config.js", "jest.setup.js"],
    rules: {
      "@typescript-eslint/no-require-imports": "off",
    },
  },
  {
    // Stylistic smells kept visible as warnings rather than build-blocking errors.
    // `no-explicit-any` fires mostly on idiomatic Recharts/ECharts/TanStack-Table
    // callback params; typing every one adds churn without changing behaviour.
    // `no-unescaped-entities` flags apostrophes in copy that render correctly.
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "react/no-unescaped-entities": "warn",
      // React-Compiler advisory heuristic. Fires on valid mounted-guard and
      // set-status-on-invalid-input patterns in the auth/chat components; kept as
      // a warning rather than restructuring working code. (Genuine impure-render
      // issues, e.g. Math.random() during render, were fixed directly.)
      "react-hooks/set-state-in-effect": "warn",
    },
  },
]);

export default eslintConfig;
