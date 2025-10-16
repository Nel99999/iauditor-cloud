// @ts-nocheck
import BottomSheet from './BottomSheet';
import useBottomSheet from '../hooks/useBottomSheet';
import Button from './Button';

export default {
  title: 'Design System/BottomSheet',
  component: BottomSheet,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'A mobile-optimized modal that slides up from the bottom with gesture support.',
      },
    },
  },
  tags: ['autodocs'],
};

// Helper component to demonstrate usage
const BottomSheetDemo = ({ snapPoint = 'half', title, children }) => {
  const { isOpen, open, close } = useBottomSheet();

  return (
    <div style={{ padding: '40px' }}>
      <Button onClick={() => open()}>Open Bottom Sheet</Button>
      <BottomSheet
        isOpen={isOpen}
        onClose={close}
        snapPoint={snapPoint}
        title={title}
      >
        {children}
      </BottomSheet>
    </div>
  );
};

// Default (Half Height)
export const Default = () => (
  <BottomSheetDemo snapPoint="half" title="Bottom Sheet">
    <div>
      <p style={{ marginBottom: '16px' }}>
        This is a bottom sheet component that slides up from the bottom of the screen.
      </p>
      <p style={{ marginBottom: '16px' }}>
        It's perfect for mobile-optimized modals, forms, and details views.
      </p>
      <p>
        You can swipe down to close or tap the backdrop.
      </p>
    </div>
  </BottomSheetDemo>
);

// Peek Height
export const PeekHeight = () => (
  <BottomSheetDemo snapPoint="peek" title="Peek View">
    <div>
      <p style={{ marginBottom: '16px' }}>
        This bottom sheet opens at 25% height (peek mode).
      </p>
      <p>
        Users can swipe up to expand to half or full height.
      </p>
    </div>
  </BottomSheetDemo>
);

// Full Height
export const FullHeight = () => (
  <BottomSheetDemo snapPoint="full" title="Full Screen">
    <div>
      <p style={{ marginBottom: '16px' }}>
        This bottom sheet opens at 90% height (full mode).
      </p>
      <p style={{ marginBottom: '16px' }}>
        Perfect for forms or detailed content.
      </p>
      <div style={{ height: '800px', background: 'linear-gradient(to bottom, transparent, rgba(0,0,0,0.05))' }}>
        <p>Scroll to see more content...</p>
      </div>
    </div>
  </BottomSheetDemo>
);

// Without Title
export const WithoutTitle = () => {
  const { isOpen, open, close } = useBottomSheet();

  return (
    <div style={{ padding: '40px' }}>
      <Button onClick={() => open()}>Open Without Title</Button>
      <BottomSheet isOpen={isOpen} onClose={close}>
        <div>
          <h3 style={{ marginBottom: '16px', fontSize: '20px', fontWeight: '600' }}>
            Custom Header
          </h3>
          <p>
            You can create your own header structure when not using the title prop.
          </p>
        </div>
      </BottomSheet>
    </div>
  );
};

// With Form
export const WithForm = () => {
  const { isOpen, open, close } = useBottomSheet();

  const handleSubmit = (e: any) => {
    e.preventDefault();
    alert('Form submitted!');
    close();
  };

  return (
    <div style={{ padding: '40px' }}>
      <Button onClick={() => open()}>Open Form</Button>
      <BottomSheet isOpen={isOpen} onClose={close} title="Contact Form" snapPoint="half">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Name</label>
            <input
              type="text"
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Email</label>
            <input
              type="email"
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '14px'
              }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Message</label>
            <textarea
              rows="4"
              required
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '14px',
                resize: 'vertical'
              }}
            />
          </div>
          <Button type="submit" variant="primary" fullWidth>
            Submit
          </Button>
        </form>
      </BottomSheet>
    </div>
  );
};

// With Long Content
export const WithLongContent = () => (
  <BottomSheetDemo snapPoint="half" title="Scrollable Content">
    <div>
      <p style={{ marginBottom: '16px' }}>
        This bottom sheet has a lot of content that requires scrolling.
      </p>
      {Array.from({ length: 20 }).map((_: any, i: number) => (
        <p key={i} style={{ marginBottom: '12px', padding: '8px', background: 'rgba(0,0,0,0.02)', borderRadius: '4px' }}>
          Content item {i + 1}
        </p>
      ))}
    </div>
  </BottomSheetDemo>
);
