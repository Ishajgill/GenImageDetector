# GenImageDetector UI

This is the web interface for testing images in a browser window.

### Development

This project is a [Node.js](https://nodejs.org/en/about) /
[React](https://react.dev/learn)

- [vite](https://vite.dev/guide/) front-end application.

You need to install Node.js for development. The best way to install
Node.js is with [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm):

- On Linux & macOS: https://github.com/nvm-sh/nvm#installing-and-updating
- On Windows: https://github.com/coreybutler/nvm-windows#installation--upgrades
  (_IMPORTANT:_ [run installer as Administrator](https://stackoverflow.com/questions/50563188/access-denied-issue-with-nvm-in-windows-10))

Once you have installed NVM, open a terminal and run:

```bash
nvm install 22 && corepack enable
pnpm install
pnpm run dev
```

You can now view the app running in your browser: http://localhost:5173.
