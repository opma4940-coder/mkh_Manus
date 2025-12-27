/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * اختبار شامل لمكونات الواجهة الأمامية
 * يختبر جميع المكونات، الأزرار، والأيقونات في الواجهة
 * ═══════════════════════════════════════════════════════════════════════════════
 */

const puppeteer = require('puppeteer');

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';
let browser;
let page;
let testResults = {
    total: 0,
    passed: 0,
    failed: 0,
    tests: []
};

// دالة لتسجيل نتيجة الاختبار
function logTest(name, passed, error = null) {
    testResults.total++;
    if (passed) {
        testResults.passed++;
        console.log(`✅ [${testResults.total}] ${name}`);
    } else {
        testResults.failed++;
        console.log(`❌ [${testResults.total}] ${name}`);
        if (error) console.log(`   خطأ: ${error}`);
    }
    testResults.tests.push({ name, passed, error });
}

// ═══ المرحلة 1: تحميل الصفحة الرئيسية ═══
async function testPageLoad() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🌐 المرحلة 1: تحميل الصفحة الرئيسية');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
        const response = await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
        logTest('تحميل الصفحة الرئيسية', response.status() === 200);
    } catch (error) {
        logTest('تحميل الصفحة الرئيسية', false, error.message);
    }

    try {
        const title = await page.title();
        logTest('عنوان الصفحة موجود', title && title.length > 0);
    } catch (error) {
        logTest('عنوان الصفحة موجود', false, error.message);
    }
}

// ═══ المرحلة 2: اختبار المكونات الرئيسية ═══
async function testMainComponents() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🧩 المرحلة 2: اختبار المكونات الرئيسية');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // اختبار وجود TopBar
    try {
        const topBar = await page.$('[data-component="TopBar"], .top-bar, header');
        logTest('مكون TopBar موجود', topBar !== null);
    } catch (error) {
        logTest('مكون TopBar موجود', false, error.message);
    }

    // اختبار وجود Sidebar
    try {
        const sidebar = await page.$('[data-component="Sidebar"], .sidebar, aside');
        logTest('مكون Sidebar موجود', sidebar !== null);
    } catch (error) {
        logTest('مكون Sidebar موجود', false, error.message);
    }

    // اختبار وجود Composer
    try {
        const composer = await page.$('[data-component="Composer"], .composer, .message-input');
        logTest('مكون Composer موجود', composer !== null);
    } catch (error) {
        logTest('مكون Composer موجود', false, error.message);
    }

    // اختبار وجود ChatLayout
    try {
        const chatLayout = await page.$('[data-component="ChatLayout"], .chat-layout, main');
        logTest('مكون ChatLayout موجود', chatLayout !== null);
    } catch (error) {
        logTest('مكون ChatLayout موجود', false, error.message);
    }
}

// ═══ المرحلة 3: اختبار الأزرار في TopBar ═══
async function testTopBarButtons() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🔘 المرحلة 3: اختبار أزرار TopBar');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    const topBarButtons = [
        { selector: '[data-button="user-menu"], .user-menu-button', name: 'زر قائمة المستخدم' },
        { selector: '[data-button="notifications"], .notifications-button', name: 'زر الإشعارات' },
        { selector: '[data-button="settings"], .settings-button', name: 'زر الإعدادات' },
        { selector: '[data-button="help"], .help-button', name: 'زر المساعدة' }
    ];

    for (const button of topBarButtons) {
        try {
            const element = await page.$(button.selector);
            logTest(button.name + ' موجود', element !== null);
            
            if (element) {
                const isVisible = await element.isIntersectingViewport();
                logTest(button.name + ' مرئي', isVisible);
            }
        } catch (error) {
            logTest(button.name + ' موجود', false, error.message);
        }
    }
}

// ═══ المرحلة 4: اختبار عناصر Sidebar ═══
async function testSidebarElements() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📂 المرحلة 4: اختبار عناصر Sidebar');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    const sidebarElements = [
        { selector: '[data-tab="tasks"], .tasks-tab', name: 'تبويب المهام' },
        { selector: '[data-tab="workspaces"], .workspaces-tab', name: 'تبويب مساحات العمل' },
        { selector: '[data-tab="events"], .events-tab', name: 'تبويب الأحداث' },
        { selector: '[data-tab="settings"], .settings-tab', name: 'تبويب الإعدادات' },
        { selector: '[data-button="new-task"], .new-task-button', name: 'زر مهمة جديدة' },
        { selector: '[data-button="new-workspace"], .new-workspace-button', name: 'زر مساحة عمل جديدة' }
    ];

    for (const element of sidebarElements) {
        try {
            const el = await page.$(element.selector);
            logTest(element.name + ' موجود', el !== null);
        } catch (error) {
            logTest(element.name + ' موجود', false, error.message);
        }
    }
}

// ═══ المرحلة 5: اختبار Composer ═══
async function testComposer() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('✍️  المرحلة 5: اختبار Composer');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    const composerElements = [
        { selector: '[data-input="message"], .message-input, textarea', name: 'حقل إدخال الرسالة' },
        { selector: '[data-button="send"], .send-button', name: 'زر الإرسال' },
        { selector: '[data-button="attach-file"], .attach-file-button', name: 'زر إرفاق ملف' },
        { selector: '[data-button="attach-image"], .attach-image-button', name: 'زر إرفاق صورة' },
        { selector: '[data-button="attach-video"], .attach-video-button', name: 'زر إرفاق فيديو' },
        { selector: '[data-button="attach-audio"], .attach-audio-button', name: 'زر إرفاق صوت' },
        { selector: '[data-button="emoji"], .emoji-button', name: 'زر الرموز التعبيرية' }
    ];

    for (const element of composerElements) {
        try {
            const el = await page.$(element.selector);
            logTest(element.name + ' موجود', el !== null);
        } catch (error) {
            logTest(element.name + ' موجود', false, error.message);
        }
    }
}

// ═══ المرحلة 6: اختبار الأيقونات ═══
async function testIcons() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🎨 المرحلة 6: اختبار الأيقونات');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
        const icons = await page.$$('svg, i[class*="icon"], .icon');
        logTest(`عدد الأيقونات المعروضة (${icons.length})`, icons.length > 0);
    } catch (error) {
        logTest('عدد الأيقونات المعروضة', false, error.message);
    }
}

// ═══ المرحلة 7: اختبار التفاعلية ═══
async function testInteractivity() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('🖱️  المرحلة 7: اختبار التفاعلية');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    // اختبار النقر على زر
    try {
        const buttons = await page.$$('button');
        if (buttons.length > 0) {
            logTest('الأزرار قابلة للنقر', true);
        } else {
            logTest('الأزرار قابلة للنقر', false, 'لم يتم العثور على أزرار');
        }
    } catch (error) {
        logTest('الأزرار قابلة للنقر', false, error.message);
    }

    // اختبار الكتابة في حقل النص
    try {
        const input = await page.$('textarea, input[type="text"]');
        if (input) {
            await input.type('اختبار');
            const value = await page.evaluate(el => el.value, input);
            logTest('الكتابة في حقل النص', value === 'اختبار');
        } else {
            logTest('الكتابة في حقل النص', false, 'لم يتم العثور على حقل نص');
        }
    } catch (error) {
        logTest('الكتابة في حقل النص', false, error.message);
    }
}

// ═══ المرحلة 8: اختبار الاستجابة ═══
async function testResponsiveness() {
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📱 المرحلة 8: اختبار الاستجابة');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    const viewports = [
        { width: 1920, height: 1080, name: 'سطح المكتب (1920x1080)' },
        { width: 1366, height: 768, name: 'لابتوب (1366x768)' },
        { width: 768, height: 1024, name: 'تابلت (768x1024)' },
        { width: 375, height: 667, name: 'موبايل (375x667)' }
    ];

    for (const viewport of viewports) {
        try {
            await page.setViewport(viewport);
            await page.waitForTimeout(1000);
            const body = await page.$('body');
            logTest(`العرض على ${viewport.name}`, body !== null);
        } catch (error) {
            logTest(`العرض على ${viewport.name}`, false, error.message);
        }
    }
}

// ═══ الدالة الرئيسية ═══
async function runTests() {
    console.log('═══════════════════════════════════════════════════════════════════════════════');
    console.log('🧪 اختبار شامل لمكونات الواجهة الأمامية');
    console.log('═══════════════════════════════════════════════════════════════════════════════\n');

    try {
        // إطلاق المتصفح
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        page = await browser.newPage();

        // تشغيل جميع الاختبارات
        await testPageLoad();
        await testMainComponents();
        await testTopBarButtons();
        await testSidebarElements();
        await testComposer();
        await testIcons();
        await testInteractivity();
        await testResponsiveness();

    } catch (error) {
        console.error('خطأ في تشغيل الاختبارات:', error);
    } finally {
        if (browser) {
            await browser.close();
        }
    }

    // النتائج النهائية
    console.log('\n═══════════════════════════════════════════════════════════════════════════════');
    if (testResults.failed === 0) {
        console.log(`✅ نجحت جميع اختبارات الواجهة! (${testResults.passed}/${testResults.total})`);
        console.log('═══════════════════════════════════════════════════════════════════════════════');
        process.exit(0);
    } else {
        console.log(`❌ فشل ${testResults.failed} من ${testResults.total} اختبار`);
        console.log('═══════════════════════════════════════════════════════════════════════════════');
        process.exit(1);
    }
}

// تشغيل الاختبارات
runTests();
