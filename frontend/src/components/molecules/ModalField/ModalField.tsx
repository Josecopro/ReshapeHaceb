import type { ReactNode } from 'react';
import './ModalField.scss';

interface ModalFieldProps {
  label: string;
  value: string | ReactNode;
  delay?: number;
}

const ModalField = ({ label, value, delay = 0 }: ModalFieldProps) => (
  <div className="modal-field" style={{ animationDelay: `${delay}s` }}>
    <div className="modal-field__label">{label}</div>
    <div className="modal-field__value">{value}</div>
  </div>
);

export default ModalField;
