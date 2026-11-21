const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');
const fs = require('fs');

const projectRoot = __dirname;
const workspaceRoot = path.resolve(projectRoot, '../..');

const config = getDefaultConfig(projectRoot);

// Ensure local empty-module exists in projectRoot (always watched and indexed by Metro)
const localEmptyModule = path.resolve(projectRoot, 'empty-module.js');
if (!fs.existsSync(localEmptyModule)) {
  fs.writeFileSync(localEmptyModule, 'module.exports = {};\n', 'utf8');
}

// Watch both project and workspace root
config.watchFolders = [projectRoot, workspaceRoot];

// Resolve node_modules from project first, then monorepo root
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, 'node_modules'),
  path.resolve(workspaceRoot, 'node_modules'),
];

// Intercept both incoming requests AND resolved file paths for empty-module
const originalResolveRequest = config.resolver.resolveRequest;

config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (typeof moduleName === 'string' && (moduleName.includes('empty-module') || moduleName.endsWith('empty-module.js'))) {
    return {
      type: 'sourceFile',
      filePath: localEmptyModule,
    };
  }

  let res;
  if (originalResolveRequest) {
    try {
      res = originalResolveRequest(context, moduleName, platform);
    } catch (err) {
      // Continue to context.resolveRequest
    }
  }
  if (!res) {
    res = context.resolveRequest(context, moduleName, platform);
  }

  // Intercept resolved result if it points to an empty-module in .pnpm
  if (
    res &&
    res.type === 'sourceFile' &&
    typeof res.filePath === 'string' &&
    (res.filePath.includes('empty-module') || res.filePath.endsWith('empty-module.js'))
  ) {
    return {
      type: 'sourceFile',
      filePath: localEmptyModule,
    };
  }

  return res;
};

module.exports = config;
