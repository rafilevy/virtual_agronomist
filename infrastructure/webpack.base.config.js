import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
    context: __dirname,
    entry: {
        main: ['react-hot-loader/patch', 'whatwg-fetch', './frontend/js/index.tsx'],
        admin: ['react-hot-loader/patch', 'whatwg-fetch', './frontend/js/admin.tsx'],
        login: ['react-hot-loader/patch', 'whatwg-fetch', './frontend/js/login.tsx'],
    },
    output: {
        // defined in local or prod
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    { loader: 'style-loader' },
                    { loader: 'css-loader' },
                    { loader: 'postcss-loader' },
                ],
            },
            {
                test: /\.scss$/,
                use: [
                    { loader: 'style-loader' },
                    { loader: 'css-loader' },
                    {
                        loader: 'postcss-loader',
                        options: {
                            sourceMap: true,
                        },
                    },
                    { loader: 'sass-loader' },
                ],
            },
            {
                test: /\.(svg)(\?v=\d+\.\d+\.\d+)?$/,
                use: [
                    {
                        loader: 'url-loader',
                        options: { limit: 100000 },
                    },
                ],
            },
            {
                test: /\.(jpg|png)?$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: { name: 'i-[hash].[ext]' },
                    },
                ],
            },
        ],
    },
    plugins: [
        // defined in local or prod
    ],
    resolve: {
        modules: ['node_modules', 'bower_components', path.resolve(__dirname, 'frontend/js/')],
        extensions: ['.tsx', '.ts', '.js', '.jsx'],
    },
};
