import type { AgentNode, AgentEdge } from './types';

// Dummy data representing a user trying to cancel a subscription with a pending debt
export const dummyNodes: AgentNode[] = [
  {
    id: 'iniciarProceso',
    label: 'Iniciar Proceso',
    tipo: 'ACCION',
    definicion: 'El usuario inicia el proceso de cancelación de su suscripción desde su cuenta.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'verificarSesion',
    label: 'Verificar Sesión',
    tipo: 'ESTADO',
    definicion: 'Sistema verifica que el usuario tenga una sesión activa y válida.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'consultarSaldo',
    label: 'Consultar Saldo Pendiente',
    tipo: 'ACCION',
    definicion: 'Sistema consulta el saldo pendiente de la cuenta para determinar si hay deudas.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'saldoCero',
    label: 'Saldo Pendiente = 0',
    tipo: 'ESTADO',
    definicion: 'El usuario no tiene saldo pendiente, puede proceder con la cancelación directamente.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'saldoPositivo',
    label: 'Saldo Pendiente > 0',
    tipo: 'ESTADO',
    definicion: 'El usuario tiene saldo pendiente, requiere pago antes de cancelar.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'ofrecerPago',
    label: 'Ofrecer Opciones de Pago',
    tipo: 'ACCION',
    definicion: 'Sistema muestra las opciones disponibles para pagar el saldo pendiente.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'pagoRealizado',
    label: 'Pago Realizado Exitosamente',
    tipo: 'ESTADO',
    definicion: 'El usuario ha completado el pago de su saldo pendiente.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'confirmarCancelacion',
    label: 'Confirmar Cancelación',
    tipo: 'ACCION',
    definicion: 'Sistema solicita confirmación explícita del usuario para proceder con la cancelación.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'cancelacionExitosa',
    label: 'Cancelación Exitosa',
    tipo: 'ESTADO',
    definicion: 'La suscripción ha sido cancelada exitosamente y el usuario recibe confirmación.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'notificarUsuario',
    label: 'Notificar al Usuario',
    tipo: 'INFORMACION',
    definicion: 'Se envía una notificación por email al usuario confirmando la cancelación.',
    agrupador_canonico: 'cancelarSuscripcion'
  },
  {
    id: 'errorSesion',
    label: 'Error de Sesión',
    tipo: 'ESTADO',
    definicion: 'No se pudo verificar la sesión del usuario, se redirige al login.',
    agrupador_canonico: 'cancelarSuscripcion'
  }
];

export const dummyEdges: AgentEdge[] = [
  {
    source: 'iniciarProceso',
    target: 'verificarSesion',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: '',
    es_bifurcacion_critica: false
  },
  {
    source: 'verificarSesion',
    target: 'consultarSaldo',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'sesion.valida === true',
    es_bifurcacion_critica: false
  },
  {
    source: 'verificarSesion',
    target: 'errorSesion',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'sesion.valida === false',
    es_bifurcacion_critica: true
  },
  {
    source: 'consultarSaldo',
    target: 'saldoCero',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'saldoPendiente === 0',
    es_bifurcacion_critica: false
  },
  {
    source: 'consultarSaldo',
    target: 'saldoPositivo',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'saldoPendiente > 0',
    es_bifurcacion_critica: true
  },
  {
    source: 'saldoCero',
    target: 'confirmarCancelacion',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: '',
    es_bifurcacion_critica: false
  },
  {
    source: 'saldoPositivo',
    target: 'ofrecerPago',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: '',
    es_bifurcacion_critica: false
  },
  {
    source: 'ofrecerPago',
    target: 'pagoRealizado',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'pago.completado === true',
    es_bifurcacion_critica: false
  },
  {
    source: 'pagoRealizado',
    target: 'confirmarCancelacion',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: '',
    es_bifurcacion_critica: false
  },
  {
    source: 'confirmarCancelacion',
    target: 'cancelacionExitosa',
    tipo_relacion: 'PROCEDURAL',
    peso: 1.0,
    condicion: 'confirmacion === true',
    es_bifurcacion_critica: false
  },
  {
    source: 'cancelacionExitosa',
    target: 'notificarUsuario',
    tipo_relacion: 'INFORMATIVA',
    peso: 0.5,
    condicion: '',
    es_bifurcacion_critica: false
  }
];