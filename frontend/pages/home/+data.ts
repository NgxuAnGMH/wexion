import { getCurrentUser } from '../../components/api';

export default async function () {
  try {
    const user = await getCurrentUser();
    return {
      user,
    };
  } catch (error) {
    // 认证失败，返回 null
    return {
      user: null,
    };
  }
}
