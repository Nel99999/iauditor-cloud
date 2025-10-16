// @ts-nocheck
import Toast, { ToastContainer } from './Toast';
import Button from './Button';

export default {
  title: 'Design System/Toast',
  component: Toast,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export const Types = () => {
  const showToast = (type, message) => {
    const event = new CustomEvent('showToast', {
      detail: { type, message }
    });
    window.dispatchEvent(event);
  };

  return (
    <>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <Button onClick={() => showToast('success', 'Success! Operation completed.')}>Show Success</Button>
        <Button onClick={() => showToast('error', 'Error! Something went wrong.')}>Show Error</Button>
        <Button onClick={() => showToast('warning', 'Warning! Please check your input.')}>Show Warning</Button>
        <Button onClick={() => showToast('info', 'Info: Here\'s some information.')}>Show Info</Button>
      </div>
      <ToastContainer />
    </>
  );
};
