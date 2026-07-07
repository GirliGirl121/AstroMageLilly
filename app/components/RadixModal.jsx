import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import './RadixModal.css';

const RadixModal = ({ isOpen, onClose, title, children }) => {
  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="radix-overlay" />
        <Dialog.Content className="radix-content">
          <header className="radix-header">
            <Dialog.Title className="radix-title">{title}</Dialog.Title>
            <div className="lilly-insignia">LILLY</div>
            <Dialog.Close className="radix-close">×</Dialog.Close>
          </header>
          <div className="radix-body">
            {children}
          </div>
          <footer className="radix-footer">
            <button className="radix-action-btn">Generate Chart</button>
            <button className="radix-action-btn">Export</button>
          </footer>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};

export default RadixModal;
