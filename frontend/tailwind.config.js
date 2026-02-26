/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{html,ts}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Roboto', 'sans-serif'],
            },
            colors: {
                primary: {
                    DEFAULT: '#4FD1C5', // Turquoise/Celeste from mockup
                    light: '#81E6D9',
                    dark: '#38B2AC',
                },
                secondary: {
                    DEFAULT: '#2C7A7B', // Darker teal for contrast
                }
            }
        },
    },
    plugins: [],
}
