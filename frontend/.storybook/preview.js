import React from 'react';
import '../src/index.css';
import '../src/design-system/tokens/base.css';
import '../src/design-system/global-modern-overrides.css';
import { ThemeProvider } from '../src/contexts/ThemeContext';

/** @type { import('@storybook/react-webpack5').Preview } */
const preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        {
          name: 'light',
          value: '#f9fafb',
        },
        {
          name: 'dark',
          value: '#111827',
        },
      ],
    },
    viewport: {
      viewports: {
        mobile: {
          name: 'Mobile',
          styles: {
            width: '390px',
            height: '844px',
          },
        },
        tablet: {
          name: 'Tablet',
          styles: {
            width: '768px',
            height: '1024px',
          },
        },
        desktop: {
          name: 'Desktop',
          styles: {
            width: '1920px',
            height: '1080px',
          },
        },
      },
    },
    layout: 'centered',
  },
  decorators: [
    (Story, context) => {
      // Apply theme based on backgrounds parameter
      const theme = context.globals.backgrounds?.value === '#111827' ? 'dark' : 'light';
      
      React.useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
      }, [theme]);

      return (
        <ThemeProvider>
          <div style={{ minHeight: '200px', padding: '20px' }}>
            <Story />
          </div>
        </ThemeProvider>
      );
    },
  ],
  globalTypes: {
    theme: {
      description: 'Global theme for components',
      defaultValue: 'light',
      toolbar: {
        title: 'Theme',
        icon: 'circlehollow',
        items: ['light', 'dark'],
        dynamicTitle: true,
      },
    },
  },
};

export default preview;