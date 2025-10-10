function setDetalle(obj, accion, usuario, fecha, just) {
  document.getElementById('d_obj').textContent = obj;
  document.getElementById('d_accion').textContent = accion;
  document.getElementById('d_user').textContent = usuario;
  document.getElementById('d_fecha').textContent = fecha;
  document.getElementById('d_just').textContent = just || '-';
  // IP de ejemplo (si quisieras pasarla también):
  document.getElementById('d_ip').textContent = '10.0.0.12';
}
