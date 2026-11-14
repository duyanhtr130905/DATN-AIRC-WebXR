import { Component, type ReactNode } from "react";
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert">Không thể tải cảnh 3D. Hãy tải lại trang; danh sách thông tin vẫn sử dụng được.</p> : this.props.children; }
}
