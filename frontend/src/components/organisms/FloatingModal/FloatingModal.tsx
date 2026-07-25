import type { ReactNode } from 'react';
import { Overlay } from '@/components/atoms';
import { ModalField } from '@/components/molecules';
import './FloatingModal.scss';

interface ModalFieldData {
  label: string;
  value: string | ReactNode;
}

interface FloatingModalProps {
  title: string;
  fields: ModalFieldData[];
  onClose: () => void;
}

const FloatingModal = ({ title, fields, onClose }: FloatingModalProps) => (
  <Overlay blur onClick={onClose} className="modal-overlay">
    <div className="modal" onClick={e => e.stopPropagation()}>
      <div className="modal__header">
        <div className="modal__title">{title}</div>
        <button className="modal__close" onClick={onClose}>×</button>
      </div>
      {fields.map((field, i) => (
        <ModalField key={i} label={field.label} value={field.value} delay={i * 0.08} />
      ))}
    </div>
  </Overlay>
);

export default FloatingModal;
